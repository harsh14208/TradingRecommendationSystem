/* ─── App defaults (used by App + TweaksPanel) ──────────────────────────────── */
/* ─── Tweaks panel ─────────────────────────────────────────────────────────── */
const DEFAULTS = {
  theme: "dark", accent: "#22d3ee", density: "comfortable",
  chartStyle: "area", aggressiveness: "balanced",
  style: "swing", days: ["Mon","Tue","Wed","Thu","Fri"],
  startTime: "09:30", endTime: "16:00",
  customConf: null,  // null = use aggressiveness preset; number = manual override
  // weight_overrides — persistent engine bias that survives Sunday factor mining runs.
  // Stored in app_settings and passed into market_ctx["weight_overrides"] each scan.
  weight_overrides: {},
};

/* ─── Owner kill-switch control ─────────────────────────────────────────────── */
function KillSwitch({ currentUser }) {
  const [paused, setPaused] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!currentUser?.is_owner) return;
    let alive = true;
    apiFetch("/api/admin/execution-kill-switch").then(d => {
      if (alive && d) setPaused(d.execution_paused);
    });
    return () => { alive = false; };
  }, [currentUser]);

  const toggle = async () => {
    setLoading(true);
    const d = await apiFetch("/api/admin/execution-kill-switch", { method: "POST" });
    if (d) setPaused(d.execution_paused);
    setLoading(false);
  };

  if (!currentUser?.is_owner || paused === null) return null;

  return (
    <button
      onClick={toggle}
      disabled={loading}
      title={paused ? "Auto-execution is paused — click to resume" : "Immediately pause all auto-execution"}
      style={{ display:"flex", alignItems:"center", gap:5, padding:"4px 10px", height:28,
        background: paused ? "var(--up-soft)" : "var(--down-soft)",
        border: `1px solid ${paused ? "color-mix(in oklch, var(--up) 35%, transparent)" : "color-mix(in oklch, var(--down) 35%, transparent)"}`,
        borderRadius:5, color: paused ? "var(--up)" : "var(--down)", fontFamily:"var(--font-mono)", fontSize:10,
        fontWeight:600, letterSpacing:"0.06em", cursor:"pointer", whiteSpace:"nowrap", opacity: loading ? 0.5 : 1 }}>
      <span style={{ width:7, height:7, borderRadius:"50%", background: paused ? "var(--up)" : "var(--down)", boxShadow: `0 0 6px ${paused ? "var(--up)" : "var(--down)"}` }}/>
      <span className="btn-text">{paused ? "RESUME AUTO-EXEC" : "KILL SWITCH"}</span>
    </button>
  );
}

/* ─── Signal quota banner ────────────────────────────────────────────────────── */
function SignalQuotaBanner({ quota, user }) {
  if (!quota || quota.limit === null) return null;
  if (user?.is_owner) return null;
  const { limit, remaining } = quota;
  const used = limit - remaining;
  const pct = Math.min(100, Math.max(0, (used / limit) * 100));
  const low = remaining <= 2 && remaining > 0;
  const exhausted = remaining <= 0;

  return (
    <div style={{
      margin:"0 14px 10px", padding:"10px 14px", borderRadius:8,
      background: exhausted ? "var(--down-soft)" : low ? "var(--warn-soft)" : "var(--bg-2)",
      border:`1px solid ${exhausted ? "color-mix(in oklch, var(--down) 35%, transparent)" : low ? "color-mix(in oklch, var(--warn) 35%, transparent)" : "var(--line)"}`,
    }}>
      <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", gap:12, fontSize:12 }}>
        <div style={{ color: exhausted ? "var(--down)" : low ? "var(--warn)" : "var(--text-dim)" }}>
          {exhausted
            ? <>You’ve viewed all <strong>{limit}</strong> free signals today.</>
            : <>Signal quota: <strong>{used}</strong> / {limit} used today</>}
        </div>
        {exhausted && (
          <button className="btn primary" style={{ fontSize:11, padding:"5px 12px" }}
            onClick={() => window.location.href="/app#pricing"}>
            Upgrade
          </button>
        )}
      </div>
      <div style={{ height:4, borderRadius:2, background:"var(--bg-1)", marginTop:8, overflow:"hidden" }}>
        <div style={{ width:`${pct}%`, height:"100%", background: exhausted ? "var(--down)" : low ? "var(--warn)" : "var(--accent)", transition:"width 0.2s" }}/>
      </div>
    </div>
  );
}

/* ─── Disclaimer ─────────────────────────────────────────────────────────────── */
const DISCLAIMER_KEY = "signal_trade_disclaimer_v1";
const TOUR_KEY = "st_tour_seen_v1";

function App() {
  /* Auth */
  const [currentUser,  setCurrentUser]  = useState(null);
  const [authReady,    setAuthReady]    = useState(false);
  const [disclaimerAck,setDisclaimerAck] = useState(() => !!localStorage.getItem(DISCLAIMER_KEY));

  /* Data — signals are pre-seeded from localStorage so the feed is visible
     on re-visits before any network request completes.                      */
  const [signals,     setSignals]     = useState(() => {
    try {
      const c = localStorage.getItem("st_signals_cache");
      if (c) {
        const parsed = JSON.parse(c);
        if (Array.isArray(parsed)) return parsed;
        localStorage.removeItem("st_signals_cache"); // discard corrupt cache
      }
    } catch {}
    return typeof SIGNALS !== "undefined" && Array.isArray(SIGNALS) ? SIGNALS : [];
  });
  const [histSignals, setHistSignals] = useState([]);
  const [log,         setLog]         = useState([]);
  const [tickerTape,  setTickerTape]  = useState(typeof TICKER_TAPE !== "undefined" ? TICKER_TAPE : []);
  const [marketCtx,   setMarketCtx]   = useState(null);
  const [signalQuota, setSignalQuota] = useState(null);
  const [online,      setOnline]      = useState(false);
  const [wsStatus,    setWsStatus]    = useState("connecting"); // connecting | open | closed
  const [lastRefresh, setLastRefresh] = useState(null);  // TSYS-11b: stale-data tracking
  const [loading,     setLoading]     = useState(true);
  const wsReconnectDelay = useRef(1000);

  /* UI state */
  const [tweakState,  setTweakState]  = useState(() => {
    try { return { ...DEFAULTS, ...JSON.parse(localStorage.getItem("st_tweaks") || "{}") }; }
    catch { return DEFAULTS; }
  });
  const [tweakSaveError, setTweakSaveError] = useState("");
  // Guard rapid setTweak calls so overlapping PUTs don't race
  const tweakSaving = useRef(false);
  const pendingTweak = useRef(null);
  const setTweak = patch => {
    const next = { ...tweakState, ...patch };
    setTweakState(next);
    setTweakSaveError(""); // clear on new save attempt
    try { localStorage.setItem("st_tweaks", JSON.stringify(next)); } catch {}
    // Persist to DB with simple in-flight guard
    pendingTweak.current = next;
    if (tweakSaving.current) return;
    const run = async () => {
      tweakSaving.current = true;
      while (pendingTweak.current) {
        const payload = pendingTweak.current;
        pendingTweak.current = null;
        try {
          await apiFetch("/api/settings", { method:"PUT", body: JSON.stringify(payload) });
        } catch (err) {
          setTweakSaveError("Could not save tweaks — try again");
          setTimeout(() => setTweakSaveError(""), 3000);
        }
      }
      tweakSaving.current = false;
    };
    run();
  };

  // Hydrate tweaks from DB on first authenticated load (DB wins over localStorage)
  const settingsHydrated = useRef(false);
  useEffect(() => {
    if (!authReady || !currentUser || settingsHydrated.current) return;
    settingsHydrated.current = true;
    apiFetch("/api/settings").then(d => {
      if (!d) return;
      const merged = { ...DEFAULTS, ...d };
      setTweakState(merged);
      try { localStorage.setItem("st_tweaks", JSON.stringify(merged)); } catch {}
    }).catch(() => {});
  }, [authReady, currentUser]);

  const [nav,            setNav]            = useState("feed");
  const [activeId,       setActiveId]       = useState(null);
  const [expandedId,     setExpandedId]     = useState(null);
  const [tweaksOpen,     setTweaksOpen]     = useState(false);
  const [accountOpen,    setAccountOpen]    = useState(false);
  const [pricingOpen,    setPricingOpen]    = useState(false);
  const [pricingContext, setPricingContext]  = useState("");
  const [now,            setNow]            = useState(() => new Date());
  const [predictive,     setPredictive]     = useState(null);
  const [predLoading,    setPredLoading]    = useState(false);
  const [paperTradeFlash,setPaperTradeFlash]= useState(false);
  const [paperSubmitting, setPaperSubmitting] = useState(false);
  const [searchQuery,    setSearchQuery]    = useState("");
  const [searchInput,    setSearchInput]    = useState("");
  const searchTimeoutRef = useRef(null);
  const [fullDetailOpen, setFullDetailOpen] = useState(false);  // kept for keyboard compat
  const [detailTab,      setDetailTab]      = useState("why"); // why | position | simulate | similar
  const [chartPeriod,    setChartPeriod]    = useState("3M");
  const [compareVs,      setCompareVs]      = useState(null);
  const btCacheRef = useRef(null);  // BacktestView 10-min result cache
  const onBtCache = useCallback(d => { btCacheRef.current = d; }, []);
  const [feedFilter,     setFeedFilter]     = useState("all");
  const [hkOpen,         setHkOpen]         = useState(false);
  const [tourOpen,       setTourOpen]       = useState(false);
  const [alertOpen,      setAlertOpen]      = useState(false);
  const [whatsNewSeen,   setWhatsNewSeen]   = useState(false);
  const [navMenuOpen,    setNavMenuOpen]    = useState(false);  // mobile nav drawer
  const [ptrState,       setPtrState]       = useState("idle");
  const ptrStartY = useRef(0);
  const feedRef = useRef(null);
  const [ariaLiveMsg,    setAriaLiveMsg]    = useState("");
  const hasUnsavedData = useRef(false);
  const searchRef       = useRef(null);
  const sidebarRef      = useRef(null);
  const deliveryRef     = useRef(null);
  useFocusTrap(navMenuOpen, () => setNavMenuOpen(false), sidebarRef);
  useFocusTrap(nav === "delivery", () => setNav("feed"), deliveryRef);

  /* Auth bootstrap — also handles ?oauth_code= redirect from Google OAuth */
  useEffect(() => {
    const ctrl = new AbortController();
    const params = new URLSearchParams(window.location.search);
    const oauthCode = params.get("oauth_code");

    if (oauthCode) {
      // Remove the code from the URL immediately (don't expose it in history)
      window.history.replaceState({}, "", window.location.pathname);
      fetch(`/api/auth/oauth-exchange?code=${oauthCode}`, { signal: ctrl.signal })
        .then(r => r.ok ? r.json() : null)
        .then(d => {
          if (d?.access_token) {
            saveToken(d.access_token);
            if (d.user) setCurrentUser(d.user);
          }
        })
        .catch(() => {})
        .finally(() => setAuthReady(true));
      return () => ctrl.abort();
    }

    const token = getToken();
    const fetchMe = () =>
      authFetch("/api/auth/me", { signal: ctrl.signal })
        .then(r => r.ok ? r.json() : null)
        .then(u => { if (u) setCurrentUser(u); else clearToken(); })
        .catch(() => {})
        .finally(() => setAuthReady(true));

    if (!token) {
      // No in-memory token after page reload — try to restore session from the
      // HTTP-only refresh cookie before giving up and sending to login.
      _tryRefresh().then(ok => { if (ok) fetchMe(); else setAuthReady(true); });
      return () => ctrl.abort();
    }
    fetchMe();
    return () => ctrl.abort();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // First-run product tour — auto-opens once, after the disclaimer is acknowledged.
  useEffect(() => {
    if (!currentUser || !disclaimerAck) return;
    if (localStorage.getItem(TOUR_KEY)) return;
    const t = setTimeout(() => setTourOpen(true), 650);
    return () => clearTimeout(t);
  }, [currentUser, disclaimerAck]);

  // Close the mobile nav drawer whenever the active view changes (a drawer item
  // was tapped) so selecting a destination dismisses the menu.
  useEffect(() => { setNavMenuOpen(false); }, [nav]);

  // P0 Fix 4: Hash-based URL state for overlays
  // On initial load, open overlay if hash matches
  useEffect(() => {
    const hash = window.location.hash.replace("#", "");
    if (!hash) return;
    const map = {
      pricing: () => setPricingOpen(true),
      tweaks: () => setTweaksOpen(true),
      alerts: () => setAlertOpen(true),
      account: () => setAccountOpen(true),
      menu: () => setNavMenuOpen(true),
      help: () => setHkOpen(true),
      tour: () => setTourOpen(true),
      screener: () => setNav("screener"),
      watchlist: () => setNav("watchlist"),
      backtest: () => setNav("backtest"),
      rules: () => setNav("rules"),
      history: () => setNav("history"),
      overview: () => setNav("overview"),
      sectors: () => setNav("sectors"),
      calendar: () => setNav("calendar"),
      paper: () => setNav("paper"),
      performance: () => setNav("performance"),
      delivery: () => setNav("delivery"),
    };
    if (map[hash]) map[hash]();
  }, []);

  // Listen to popstate/hashchange to close overlays when user clicks Back
  useEffect(() => {
    const onPop = () => {
      const hash = window.location.hash.replace("#", "");
      if (!hash) {
        setPricingOpen(false);
        setTweaksOpen(false);
        setAlertOpen(false);
        setAccountOpen(false);
        setNavMenuOpen(false);
        setHkOpen(false);
        setTourOpen(false);
        if (["screener","watchlist","backtest","rules","alerts","history","overview","sectors","calendar","paper","performance","delivery"].includes(nav)) {
          setNav("feed");
        }
      } else {
        const map = {
          pricing: () => setPricingOpen(true),
          tweaks: () => setTweaksOpen(true),
          alerts: () => setAlertOpen(true),
          account: () => setAccountOpen(true),
          menu: () => setNavMenuOpen(true),
          help: () => setHkOpen(true),
          tour: () => setTourOpen(true),
          screener: () => setNav("screener"),
          watchlist: () => setNav("watchlist"),
          backtest: () => setNav("backtest"),
          rules: () => setNav("rules"),
          history: () => setNav("history"),
          overview: () => setNav("overview"),
          sectors: () => setNav("sectors"),
          calendar: () => setNav("calendar"),
          paper: () => setNav("paper"),
          performance: () => setNav("performance"),
          delivery: () => setNav("delivery"),
        };
        if (map[hash]) map[hash]();
      }
    };
    window.addEventListener("popstate", onPop);
    window.addEventListener("hashchange", onPop);
    return () => {
      window.removeEventListener("popstate", onPop);
      window.removeEventListener("hashchange", onPop);
    };
  }, [nav]);

  // Update hash when overlay state changes
  useEffect(() => {
    const active = (() => {
      if (pricingOpen) return "pricing";
      if (tweaksOpen) return "tweaks";
      if (alertOpen) return "alerts";
      if (accountOpen) return "account";
      if (navMenuOpen) return "menu";
      if (hkOpen) return "help";
      if (tourOpen) return "tour";
      if (nav === "screener") return "screener";
      if (nav === "watchlist") return "watchlist";
      if (nav === "backtest") return "backtest";
      if (nav === "rules") return "rules";
      if (nav === "alerts") return "alerts";
      if (nav === "history") return "history";
      if (nav === "overview") return "overview";
      if (nav === "sectors") return "sectors";
      if (nav === "calendar") return "calendar";
      if (nav === "paper") return "paper";
      if (nav === "performance") return "performance";
      if (nav === "delivery") return "delivery";
      return "";
    })();
    if (active) {
      if (window.location.hash !== `#${active}`) {
        window.location.hash = active;
      }
    } else {
      if (window.location.hash) {
        window.history.replaceState(null, "", window.location.pathname + window.location.search);
      }
    }
  }, [pricingOpen, tweaksOpen, alertOpen, accountOpen, navMenuOpen, hkOpen, tourOpen, nav]);

  // Warn before leaving if unsaved form data exists
  useEffect(() => {
    const handler = (e) => {
      if (hasUnsavedData.current) {
        e.preventDefault();
        e.returnValue = "You have unsaved changes. Are you sure you want to leave?";
      }
    };
    window.addEventListener("beforeunload", handler);
    return () => window.removeEventListener("beforeunload", handler);
  }, []);

  /* ── WebSocket Connection ── */
  useEffect(() => {
    if (!authReady || !currentUser) return;
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const token = getToken();
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    let ws = null;
    let reconnectTimer = null;
    let alive = true;

    const connect = () => {
      if (!alive) return;
      setWsStatus("connecting");
      ws = token ? new WebSocket(wsUrl, ["token", token]) : new WebSocket(wsUrl);

      ws.onopen = () => {
        if (!alive) return;
        setWsStatus("open");
        wsReconnectDelay.current = 1000; // reset backoff on success
      };

      ws.onmessage = (e) => {
        try {
          const data = JSON.parse(e.data);
          if (data.type === "new_signal") {
            setSignals(prev => [data.signal, ...prev.filter(s => s.id !== data.signal.id)]);
            setAriaLiveMsg(`New ${data.signal.action} signal for ${data.signal.ticker} at $${fmt(data.signal.price)}`);
            setTimeout(() => setAriaLiveMsg(""), 3000);
          } else if (data.type === "price_update") {
            if (data.quotes) setTickerTape(data.quotes);
          } else if (data.type === "tick") {
            setTickerTape(prev => {
              const idx = prev.findIndex(t => t.t === data.ticker);
              if (idx === -1) return prev;
              const next = [...prev];
              next[idx] = { ...next[idx], p: data.price };
              return next;
            });
          } else if (data.type === "market_context") {
            setMarketCtx(data.data);
          }
        } catch (err) {}
      };

      ws.onerror = () => {
        if (!alive) return;
        setWsStatus("closed");
      };

      ws.onclose = () => {
        if (!alive) return;
        setWsStatus("closed");
        // Exponential backoff reconnection, capped at 30s
        const delay = Math.min(wsReconnectDelay.current, 30000);
        wsReconnectDelay.current = delay * 1.5;
        reconnectTimer = setTimeout(connect, delay);
      };
    };

    connect();

    return () => {
      alive = false;
      if (reconnectTimer) clearTimeout(reconnectTimer);
      if (ws) {
        ws.onopen = null;
        ws.onmessage = null;
        ws.onerror = null;
        ws.onclose = null;
        ws.close();
      }
    };
  }, [authReady, currentUser]);

  /* Theme */
  useEffect(() => {
    document.documentElement.setAttribute("data-theme",   tweakState.theme);
    document.documentElement.setAttribute("data-density", tweakState.density);
    document.documentElement.style.setProperty("--accent", tweakState.accent);
  }, [tweakState]);

  /* Clock */
  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(id);
  }, []);

  /* Derived */
  // customConf (set via RulesView input) overrides the aggressiveness preset
  const threshold = tweakState.customConf != null
    ? tweakState.customConf
    : tweakState.aggressiveness === "aggressive" ? 55
    : tweakState.aggressiveness === "conservative" ? 75 : 62;
  // ── Natural Language Signal Search ──────────────────────────────────────────
  // Parses intent from plain-English queries beyond simple ticker/company matches.
  // Examples: "dark pool buy", "oversold tech", "high confidence sell", "RSI divergence"
  const _parseNLQuery = useCallback((q) => {
    if (!q) return null;
    const lq = q.toLowerCase();
    const filters = {};

    // Action intent
    if (/\bbuy\b|\bbull/i.test(lq))  filters.action = "BUY";
    if (/\bsell\b|\bshort\b|\bbear/i.test(lq)) filters.action = "SELL";

    // Confidence intent
    if (/high.conf|strong|conviction|≥75|75%|above.70/i.test(lq)) filters.minConf = 75;
    if (/low.conf|weak|below.60/i.test(lq)) filters.maxConf = 60;

    // Style intent
    if (/\bswing\b/i.test(lq))    filters.style = "swing";
    if (/\bposition\b|\blong.term/i.test(lq)) filters.style = "position";
    if (/\bintraday\b|\bday.trade/i.test(lq)) filters.style = "intraday";

    // Source/signal intent — match against rationale/sources
    if (/dark.pool|block.trade|finra|massive/i.test(lq)) filters.source = "Dark Pool";
    if (/13f|institutional|hedge.fund/i.test(lq)) filters.source = "13F";
    if (/insider/i.test(lq)) filters.source = "SEC EDGAR";
    if (/rsi|oscillator|oversold|overbought/i.test(lq)) filters.rationale = "RSI";
    if (/macd|crossover/i.test(lq)) filters.rationale = "MACD";
    if (/earnings|eps/i.test(lq)) filters.source = "Earnings";
    if (/options|sweep|gamma/i.test(lq)) filters.source = "Options";
    if (/fundamentals?|f.score|piotroski|fcf/i.test(lq)) filters.source = "Fundamentals";
    if (/macro|vix|yield.curve|fed/i.test(lq)) filters.source = "Macro";

    // Sector intent — match against sectorEtf
    const sectorMap = {tech:"XLK",financials:"XLF",energy:"XLE",healthcare:"XLV",
      consumer:"XLY",materials:"XLB",utilities:"XLU",industrial:"XLI",realestate:"XLRE"};
    for (const [kw, etf] of Object.entries(sectorMap)) {
      if (lq.includes(kw)) { filters.sector = etf; break; }
    }

    return Object.keys(filters).length > 0 ? filters : null;
  }, []);

  const matchesSearch = useCallback((s) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();

    // Simple ticker / company match (priority)
    if ((s.ticker || "").toLowerCase().includes(q) ||
        (s.company || "").toLowerCase().includes(q)) return true;

    // Natural language query parsing
    const nlFilters = _parseNLQuery(searchQuery);
    if (!nlFilters) return false;  // non-ticker query didn't parse — no match

    const checks = [
      !nlFilters.action  || s.action === nlFilters.action,
      !nlFilters.style   || s.style  === nlFilters.style,
      !nlFilters.minConf || (s.confidence || 0) >= nlFilters.minConf,
      !nlFilters.maxConf || (s.confidence || 0) <= nlFilters.maxConf,
      !nlFilters.sector  || s.sectorEtf === nlFilters.sector,
      !nlFilters.source  || (s.sources || []).includes(nlFilters.source),
      !nlFilters.rationale || (s.rationale || []).some(r =>
        (r.head || "").toLowerCase().includes(nlFilters.rationale.toLowerCase())
      ),
    ];
    return checks.every(Boolean);
  }, [searchQuery, _parseNLQuery]);

  const styleFilter = tweakState.style; // "intraday" | "swing" | "position"
  const filteredSignals = useMemo(() => {
    let sigs = signals.filter(s => (s.confidence || 0) >= threshold && matchesSearch(s));
    // Style strip filter — only show signals matching selected trading style
    if (styleFilter) sigs = sigs.filter(s => !s.style || s.style === styleFilter);
    if (feedFilter === "buy")  sigs = sigs.filter(s => s.action === "BUY");
    if (feedFilter === "sell") sigs = sigs.filter(s => s.action === "SELL");
    if (feedFilter === "high") sigs = sigs.filter(s => (s.confidence || 0) >= 75);
    return sigs;
  }, [signals, threshold, matchesSearch, feedFilter, styleFilter]);
  const suppressedSignals = useMemo(() =>
    signals.filter(s => (s.confidence || 0) < threshold && matchesSearch(s) && (!s.style || s.style === styleFilter)),
    [signals, threshold, matchesSearch, styleFilter]
  );

  // ── DOM Load-More pagination ──────────────────────────────────────────────
  // Render 30 cards initially; each "Show more" reveals 20 more.
  // Avoids rendering 100+ SVG sparklines at once, which tanks scroll FPS.
  const FEED_PAGE = 30;
  const SUPPRESSED_PAGE = 20;
  const [feedLimit, setFeedLimit] = useState(FEED_PAGE);
  const [suppressedLimit, setSuppressedLimit] = useState(SUPPRESSED_PAGE);
  // Reset page when filters change so new results show from the top
  useEffect(() => {
    setFeedLimit(FEED_PAGE);
    setSuppressedLimit(SUPPRESSED_PAGE);
  }, [feedFilter, styleFilter, threshold, searchQuery]);
  const visibleSignals   = filteredSignals.slice(0, feedLimit);
  const hiddenCount      = filteredSignals.length - visibleSignals.length;
  const visibleSuppressed = suppressedSignals.slice(0, suppressedLimit);
  const hiddenSuppressed  = suppressedSignals.length - visibleSuppressed.length;

  const active = signals.find(s => s.id === activeId) || filteredSignals[0] || signals[0];

  // Live price for the active signal — updated from WebSocket tick messages.
  // tickerTape is already updated by the WS handler; derive livePrice from it.
  const livePrice = useMemo(() => {
    if (!active?.ticker) return null;
    const t = (tickerTape || []).find(t => (t.t || t.ticker) === active.ticker);
    return t ? (t.p || t.price || null) : null;
  }, [tickerTape, active?.ticker]);

  // Precompute outcome lookup so OutcomeStrip never runs .filter on the full array.
  // O(n) once on histSignals change; O(1) lookup per signal card render.
  const outcomeByTicker = useMemo(() => {
    const m = {};
    for (const h of histSignals) {
      if (h.outcomePct == null && h.outcome14d == null) continue;
      (m[h.ticker] ??= []).push(h);
    }
    return m;
  }, [histSignals]);

  // Reset detail tab when active signal changes so each signal opens fresh at "Why".
  useEffect(() => { setDetailTab("why"); }, [activeId]);

  /* ── Mobile horizontal panel paging ─────────────────────────────────────── */
  const mainRef = useRef(null);
  const [panelIdx, setPanelIdx] = useState(0);
  const panelCount = 2 + (active ? 1 : 0); // feed + detail + delivery

  // Keep the active dot in sync with swipe scrolling.
  useEffect(() => {
    const m = mainRef.current;
    if (!m) return;
    const onScroll = () => {
      const idx = Math.min(panelCount - 1, Math.max(0, Math.round(m.scrollLeft / Math.max(1, m.clientWidth))));
      setPanelIdx(idx);
    };
    m.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
    return () => m.removeEventListener('scroll', onScroll);
  }, [panelCount]);

  // Clamp the current index if the number of panels changes (e.g. no active signal).
  useEffect(() => {
    setPanelIdx(prev => Math.min(prev, panelCount - 1));
  }, [panelCount]);

  const scrollToPanel = (idx) => {
    const m = mainRef.current;
    if (!m) return;
    const target = Math.max(0, Math.min(idx, panelCount - 1));
    m.scrollTo({ left: m.clientWidth * target, behavior: 'smooth' });
    setPanelIdx(target);
  };

  /* Keyboard shortcuts: ⌘K, d, p, s, ?, Esc, ⌘\, 1-4 */
  useEffect(() => {
    const handler = e => {
      const tag = document.activeElement?.tagName;
      const typing = tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT";

      if (e.key === "?" || (e.shiftKey && e.key === "/")) { e.preventDefault(); setHkOpen(v => !v); return; }
      if (e.key === "Escape") { if (navMenuOpen) { setNavMenuOpen(false); return; } if (tourOpen) { setTourOpen(false); return; } if (!whatsNewSeen) { setWhatsNewSeen(true); return; } setHkOpen(false); if (!hkOpen) setFullDetailOpen(false); return; }
      if ((e.metaKey || e.ctrlKey) && e.key === "\\") { e.preventDefault(); setTweak({ density: tweakState.density === "compact" ? "comfortable" : "compact" }); return; }
      if (!typing && e.key === "1") { setFeedFilter("all");  return; }
      if (!typing && e.key === "2") { setFeedFilter("buy");  return; }
      if (!typing && e.key === "3") { setFeedFilter("sell"); return; }
      if (!typing && e.key === "4") { setFeedFilter("high"); return; }
      // j/k navigation through signal feed
      if (!typing && (e.key === "j" || e.key === "k") && filteredSignals.length > 0) {
        e.preventDefault();
        const idx = filteredSignals.findIndex(s => s.id === activeId);
        const next = e.key === "j"
          ? filteredSignals[Math.min(idx + 1, filteredSignals.length - 1)]
          : filteredSignals[Math.max(idx - 1, 0)];
        if (next) { setActiveId(next.id); setExpandedId(null); }
        return;
      }
      // Enter — open full detail for active signal
      if (!typing && e.key === "Enter" && activeId) { e.preventDefault(); setFullDetailOpen(true); return; }
      // Shift+S — send active signal to Telegram
      if (!typing && e.shiftKey && e.key === "S" && active) { e.preventDefault(); sendToTelegram(active.id); return; }

      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        searchRef.current?.focus();
        searchRef.current?.select();
        return;
      }
      if (!typing && e.key === "d") {
        e.preventDefault();
        setFullDetailOpen(v => !v);
        return;
      }
      // Paper Trade shortcut (P) — only when a signal is selected and detail is open
      if (!typing && e.key === "p" && active && activeId) {
        e.preventDefault();
        // Check Basic tier access for paper trading
        if (!hasTierAccess(currentUser.subscription_tier, "basic", currentUser.is_owner)) {
          setPricingContext("Paper trading requires Basic or higher.");
          setPricingOpen(true);
          return;
        }
        // Execute paper trade
        const side = active.action === "BUY" ? "buy" : "sell";
        const qty = 1; // Default 1 share for paper trade
        authFetch("/api/paper/orders", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            symbol: active.ticker,
            qty,
            side,
            type: "market",
            time_in_force: "day",
          }),
        }).then(res => {
          if (res && res.ok) {
            // Show success feedback via React state (no DOM mutation)
            setPaperTradeFlash(true);
            setTimeout(() => setPaperTradeFlash(false), 1500);
          }
        });
        return;
      }
      // Skip signal shortcut (S) — only when a signal is selected
      if (!typing && e.key === "s" && active && activeId) {
        e.preventDefault();
        skipSignal(activeId);
        return;
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [active, activeId, currentUser, tweakState.density, filteredSignals, hkOpen, tourOpen, navMenuOpen]);

  /* ── Clock state — always New York time, DST-aware ── */
  // "16:32:07"
  const etClock = _etFmt(now, { hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false });

  // "EDT" or "EST" — parse from the formatted timezone name part
  const etAbbr = (() => {
    try {
      const parts = new Intl.DateTimeFormat("en-US", {
        timeZone: "America/New_York", timeZoneName: "short",
        hour: "numeric",
      }).formatToParts(now);
      return parts.find(p => p.type === "timeZoneName")?.value || "ET";
    } catch { return "ET"; }
  })();

  // "UTC-4" (EDT) or "UTC-5" (EST) — computed from actual NY vs UTC offset
  const etOffset = (() => {
    try {
      const parts = new Intl.DateTimeFormat("en-US", {
        timeZone: "America/New_York", timeZoneName: "shortOffset",
        hour: "numeric",
      }).formatToParts(now);
      const gmt = parts.find(p => p.type === "timeZoneName")?.value || "GMT-4";
      return gmt.replace("GMT", "UTC");
    } catch {
      // Fallback: compute numerically
      const nyMs  = new Date(now.toLocaleString("en-US", { timeZone: "America/New_York" })).getTime();
      const diff  = Math.round((nyMs - now.getTime()) / 3600000);
      return `UTC${diff >= 0 ? "+" : ""}${diff}`;
    }
  })();

  // User's local time for hover tooltip
  const localClock = now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false });
  const localTz    = Intl.DateTimeFormat().resolvedOptions().timeZone;

  const [refreshing,   setRefreshing]   = useState(false);
  const [countdown,    setCountdown]    = useState(30);

  const _parseQuotaHeaders = (headers) => {
    const limit = headers.get("X-Signal-Quota-Limit");
    const remaining = headers.get("X-Signal-Quota-Remaining");
    const resetsAt = headers.get("X-Signal-Quota-Resets-At");
    if (!limit || !remaining) return null;
    return {
      limit: limit === "unlimited" ? null : parseInt(limit, 10),
      remaining: remaining === "unlimited" ? null : parseInt(remaining, 10),
      resetsAt: resetsAt || null,
    };
  };

  const loadData = useCallback(async (showSpinner = false, opts = {}) => {
    if (showSpinner) setRefreshing(true);
    const signal = opts.signal;

    // ── Tier 1: fast DB-only reads — clears loading immediately ──────────────
    try {
      const sigsRaw = await apiFetchRaw("/api/signals", { signal });
      const sigs = sigsRaw.json;
      if (Array.isArray(sigs)) {
        setSignals(sigs);
        try { localStorage.setItem("st_signals_cache", JSON.stringify(sigs)); } catch {}
      }
      if (sigsRaw.ok) setSignalQuota(_parseQuotaHeaders(sigsRaw.headers));
      setOnline(true);
      setLastRefresh(new Date());  // TSYS-11b
    } catch {
      setOnline(false);
    } finally {
      setLoading(false);          // feed is visible after this point
      if (showSpinner) setRefreshing(false);
    }

    // ── Tier 2: enrichment — loads in background after feed is shown ─────────
    Promise.all([
      apiFetch("/api/delivery/log", { signal }),
      apiFetch("/api/quotes", { signal }),
      apiFetch("/api/market/context", { signal }),
      apiFetch("/api/signals/history", { signal }),
    ]).then(([lg, quotes, mktCtx, hist]) => {
      if (Array.isArray(lg))     setLog(lg);
      if (Array.isArray(quotes)) setTickerTape(quotes);
      if (mktCtx) setMarketCtx(mktCtx);
      if (hist)   setHistSignals(Array.isArray(hist) ? hist.filter(h => h.outcomePct != null) : []);
    }).catch(() => {});
  }, []);

  /* Initial data load — only fires if the auth bootstrap didn't already
     trigger loadData (i.e. no token was present on mount).                */
  useEffect(() => {
    if (!authReady || !currentUser) return;
    const ctrl = new AbortController();
    loadData(false, { signal: ctrl.signal });
    return () => ctrl.abort();
  }, [authReady, currentUser, loadData]);

  /* Auto-refresh every 30 seconds + countdown ticker */
  useEffect(() => {
    if (!authReady || !currentUser) return;
    const INTERVAL = 30;
    setCountdown(INTERVAL);
    const tick = setInterval(() => {
      setCountdown(c => {
        if (c <= 1) { loadData(); return INTERVAL; }
        return c - 1;
      });
    }, 1000);
    return () => clearInterval(tick);
  }, [authReady, currentUser, loadData]);

  /* Fetch predictive data whenever the active signal changes */
  useEffect(() => {
    if (!currentUser || !active) { setPredictive(null); return; }
    setPredLoading(true);
    setPredictive(null);
    const ctrl = new AbortController();
    const params = new URLSearchParams({
      action:     active.action,
      confidence: active.confidence || 65,
      sources:    (active.sources || []).join(","),
      style:      active.style || "swing",
    });
    apiFetch(`/api/signals/predictive?${params}`, { signal: ctrl.signal })
      .then(d => { if (d) setPredictive(d); })
      .finally(() => setPredLoading(false));
    return () => ctrl.abort();
  }, [activeId]);

  useEffect(() => {
    if (!activeId && filteredSignals.length > 0) {
      setActiveId(filteredSignals[0].id);
    } else if (activeId && filteredSignals.length > 0 && !filteredSignals.find(s => s.id === activeId)) {
      // Active signal filtered out (e.g. style changed) — select first visible
      setActiveId(filteredSignals[0].id);
      setExpandedId(null);
    }
  }, [activeId, filteredSignals]);

  const up = active ? (active.change || 0) >= 0 : true;

  /* Actions */
  const sendToTelegram = async (id) => {
    const sig = signals.find(s => s.id === id) || active;
    if (!sig) return;
    try {
      const raw = await authFetch(`/api/signals/${sig.id}/send`, { method:"POST" });
      const data = await raw.json();
      if (!raw.ok) {
        // Show the server's error message (e.g. "Telegram not linked")
        alert(data.detail || "Could not send to Telegram.");
        return;
      }
      if (data.success) {
        const _etNow = _etFmt(new Date(), { hour:"2-digit", minute:"2-digit", second:"2-digit", hour12:false });
        setLog(prev => [{ time:_etNow, status:"sent", message:`✓ ${sig.action} ${sig.ticker} @ ${fmt(sig.price)} (Conf ${(sig.confidence||0).toFixed(0)}%)`, created_at: new Date().toISOString() }, ...prev]);
      } else {
        alert(data.detail || "Telegram delivery failed. Check your bot token.");
      }
    } catch {
      alert("Network error — could not reach the server.");
    }
  };

  const skipSignal = async (id) => {
    await apiFetch(`/api/signals/${id}/skip`, { method:"POST" });
    setSignals(prev => prev.filter(s => s.id !== id));
    if (activeId === id) setActiveId(null);
    if (expandedId === id) setExpandedId(null);
  };

  const reviewSignal = async (id) => {
    await apiFetch(`/api/signals/${id}/review`, { method:"POST" });
    setSignals(prev => prev.map(s => s.id === id ? { ...s, reviewed: true } : s));
  };

  const saveNote = async (id, note) => {
    await apiFetch(`/api/signals/${id}/notes`, { method:"PATCH", body: JSON.stringify({ notes: note }) });
    setSignals(prev => prev.map(s => s.id === id ? { ...s, notes: note } : s));
  };


  const manualScan = async () => {
    setRefreshing(true);
    await apiFetch("/api/signals/scan", { method:"POST" });
    // Give the backend 1.5s to process then pull fresh data
    await new Promise(r => setTimeout(r, 1500));
    await loadData(false);
    setRefreshing(false);
  };

  const handleLogout = () => {
    authFetch("/api/auth/logout", { method:"POST" }).finally(() => {
      clearToken();
      window.location.replace("/login");
    });
  };

  /* Auth gate — redirect side-effect must live in useEffect, not render */
  useEffect(() => {
    if (authReady && !currentUser) {
      window.location.replace("/login?next=/app");
    }
  }, [authReady, currentUser]);

  if (!authReady) return (
    <div style={{ display:"flex", alignItems:"center", justifyContent:"center", height:"100vh", background:"var(--bg-0)", color:"var(--text-faint)", fontFamily:"var(--font-mono)", fontSize:13 }}>Loading…</div>
  );
  if (!currentUser) return null;

  /* Disclaimer */
  if (!disclaimerAck) return (
    <div style={{ position:"fixed", inset:0, zIndex:9999, background:"rgba(0,0,0,0.82)", display:"flex", alignItems:"center", justifyContent:"center", padding:20 }}>
      <div style={{ background:"var(--bg-1)", border:"1px solid var(--line)", borderRadius:14, maxWidth:560, width:"100%", padding:"32px 36px" }}>
        <div style={{ fontSize:18, fontWeight:700, marginBottom:16 }}>⚠️ Important Disclaimer</div>
        <div style={{ fontSize:13, lineHeight:1.75, color:"var(--text-dim)", display:"flex", flexDirection:"column", gap:10 }}>
          <p style={{ margin:0 }}><strong style={{ color:"var(--text)" }}>Signal.Trade is not financial advice.</strong> All signals are for informational and educational purposes only.</p>
          <p style={{ margin:0 }}>Signal.Trade is <strong style={{ color:"var(--text)" }}>not a registered investment adviser</strong>. Nothing here constitutes a solicitation to buy or sell any security.</p>
          <p style={{ margin:0 }}><strong style={{ color:"var(--warn)" }}>Trading involves substantial risk of loss.</strong> Past performance does not guarantee future results. You are solely responsible for all investment decisions.</p>
        </div>
        <button className="btn primary" style={{ width:"100%", marginTop:24, padding:"11px 0", fontSize:13, fontWeight:700, textAlign:"center", justifyContent:"center" }}
          onClick={() => { localStorage.setItem(DISCLAIMER_KEY,"1"); setDisclaimerAck(true); }}>
          I understand — this is for personal research only
        </button>
      </div>
    </div>
  );

  return (
    <div className="app">
      <a href="#main-content" className="skip-link">Skip to main content</a>
      <h1 style={{ position:"absolute", width:"1px", height:"1px", padding:0, margin:"-1px", overflow:"hidden", clip:"rect(0,0,0,0)", whiteSpace:"nowrap", border:0 }}>Signal.Trade Dashboard</h1>
      <div aria-live="polite" aria-atomic="true" className="visually-hidden">
        {ariaLiveMsg}
      </div>
      {/* ── Top bar ── */}
      <div className="topbar">
        <div className="brand">
          <img src="/logo-full.svg" alt="Signal.Trade" style={{ height: 95, width: "auto" }}/>
          <span className="faint mono" style={{ fontWeight:400, marginLeft:8, fontSize:10 }}>v5.2</span>
        </div>
        <div className="search" onClick={() => searchRef.current?.focus()} style={{ cursor:"text" }}>
          <Icon name="search" size={12}/>
          <input
            ref={searchRef}
            type="text"
            placeholder="Search tickers or type: 'dark pool buy', 'oversold tech', 'high conf sell'…"
            value={searchInput}
            onChange={e => {
              setSearchInput(e.target.value);
              if (searchTimeoutRef.current) clearTimeout(searchTimeoutRef.current);
              searchTimeoutRef.current = setTimeout(() => setSearchQuery(e.target.value), 300);
            }}
            onKeyDown={e => {
              if (e.key === "Escape") {
                setSearchInput("");
                setSearchQuery("");
              }
            }}
            style={{ background:"none", border:"none", outline:"none", flex:1,
              color:"var(--text)", fontFamily:"var(--font-mono)", fontSize:"var(--fs-sm)",
              padding:0, minWidth:0 }}
          />
          {searchInput
            ? <button onClick={e => { e.stopPropagation(); setSearchInput(""); setSearchQuery(""); }}
                style={{ padding:0, lineHeight:1, fontSize:15, color:"var(--text-faint)" }}>×</button>
            : <span><span className="kbd">⌘K</span></span>
          }
        </div>
        <div className="ticker">
          <div className="ticker-track">
            {[...(tickerTape||[]),...(tickerTape||[])].map((t, i) => (
              <span key={i}><strong>{t.t||t.ticker}</strong>{fmt(t.p||t.price, (t.p||t.price) > 1000 ? 0 : 2)} <span className={(t.c||t.change||0) >= 0 ? "up" : "down"}>{sgn(t.c||t.change||0)}{fmt(Math.abs(t.c||t.change||0), 2)}</span></span>
            ))}
          </div>
        </div>
        <div className="topbar-actions">
          {online && marketCtx?.macro && (() => {
            const hmm = marketCtx.hmm_regime;
            const label = hmm?.regime ?? ((marketCtx.macro.spx_vs_50d||0)>=0?"bull":"bear");
            const prob  = hmm ? (label === "bull" ? hmm.bull_prob : hmm.bear_prob) : null;
            const transRisk = hmm?.transition_risk ?? 0;
            const color = label === "bull" ? "var(--up)" : label === "bear" ? "var(--down)" : "var(--warn)";
            const tip = hmm
              ? `HMM: ${label.toUpperCase()} — P(bull)=${(hmm.bull_prob*100).toFixed(0)}% P(bear)=${(hmm.bear_prob*100).toFixed(0)}% · Trans.risk=${(transRisk*100).toFixed(0)}% · VIXz=${hmm.vix_z??0}σ`
              : `SPX ${(marketCtx.macro.spx_vs_50d||0)>=0?"above":"below"} 50-DMA · VIX ${marketCtx.macro.vix?.toFixed(1)||"—"}`;
            return (
              <span className="chip" title={tip} style={{ borderColor: transRisk > 0.20 ? "var(--warn)" : undefined }}>
                <span style={{ width:6, height:6, borderRadius:"50%", background:color, boxShadow:`0 0 6px ${color}` }}/>
                {hmm ? "HMM" : ""} REGIME · {label.toUpperCase()}
                {prob != null && <span style={{ marginLeft:4, opacity:0.65, fontSize:9 }}>{(prob*100).toFixed(0)}%</span>}
                {transRisk > 0.20 && <span style={{ marginLeft:4, color:"var(--warn)", fontSize:9 }}>⚠</span>}
              </span>
            );
          })()}
          {online && (
            <span className="chip">
              <span style={{ width:6, height:6, borderRadius:"50%", background:"var(--up)", boxShadow:"0 0 6px var(--up)" }}/>
              NYSE {marketCtx?.macro?.market_open !== false ? "OPEN" : "CLOSED"}
            </span>
          )}
          <span className="chip mono" title={`Your local time: ${localClock} (${localTz})`}>
            {etClock} {etAbbr}
          </span>
          <button className="iconbtn hamburger-btn"
            onClick={() => {
              // Mobile: open the full navigation drawer (the bottom bar only shows
              // 6 of ~16 destinations). Desktop: toggle row density as before.
              if (typeof window !== "undefined" && window.innerWidth <= 768) setNavMenuOpen(v => !v);
              else setTweak({ density: tweakState.density === "compact" ? "comfortable" : "compact" });
            }}
            aria-label="Menu"
            title="Menu / density (⌘\\)"
            style={{ minWidth: 44, minHeight: 44 }}>
            <svg aria-hidden="true" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/>{tweakState.density==="compact"&&<><line x1="3" y1="9" x2="21" y2="9" opacity="0.4"/><line x1="3" y1="15" x2="21" y2="15" opacity="0.4"/></>}</svg>
          </button>
          <button className="iconbtn" onClick={() => setHkOpen(true)} title="Keyboard shortcuts (?)">
            <span style={{ fontFamily:"var(--font-mono)", fontSize:11, fontWeight:600 }}>?</span>
          </button>
          <button className={`iconbtn ${refreshing ? "active" : ""}`} onClick={manualScan}
            title={`Refresh signals — auto-refreshes in ${countdown}s`}
            disabled={refreshing}>
            <span style={{ display:"inline-block", animation: refreshing ? "spin 0.8s linear infinite" : "none" }}>
              <Icon name="refresh"/>
            </span>
          </button>
          <span className="chip mono" style={{ fontSize:9, opacity: refreshing ? 0.4 : 0.7, minWidth:28, textAlign:"center" }}
            title="Seconds until next auto-refresh">
            {refreshing ? "…" : `${countdown}s`}
          </span>
          <KillSwitch currentUser={currentUser}/>
          <button className={`iconbtn ${tweaksOpen?"active":""}`} onClick={() => setTweaksOpen(!tweaksOpen)} aria-label="Settings"><Icon name="settings"/></button>
          <button
            onClick={handleLogout}
            title="Sign out"
            style={{ display:"flex", alignItems:"center", gap:5, padding:"4px 10px", height:28,
              background:"var(--down-soft)", border:"1px solid color-mix(in oklch, var(--down) 25%, transparent)",
              borderRadius:5, color:"var(--down)", fontFamily:"var(--font-mono)", fontSize:10,
              fontWeight:600, letterSpacing:"0.06em", cursor:"pointer", whiteSpace:"nowrap" }}>
            <svg aria-hidden="true" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
              <polyline points="16 17 21 12 16 7"/>
              <line x1="21" y1="12" x2="9" y2="12"/>
            </svg>
            <span className="btn-text">Sign out</span>
          </button>
          <button
            className="user-avatar"
            style={{ width:28, height:28, fontSize:11, cursor:"pointer",
              background:TIER_COLORS[currentUser.subscription_tier]+"33",
              border:`1px solid ${TIER_COLORS[currentUser.subscription_tier]}`,
              borderRadius:"50%", display:"flex", alignItems:"center", justifyContent:"center",
              color:"var(--text)", fontFamily:"var(--font-mono)", fontWeight:700,
            }}
            onClick={() => setAccountOpen(true)}
            title={`${currentUser.email} — click to open account settings`}>
            {(currentUser.full_name || currentUser.email || "?")[0].toUpperCase()}
          </button>
        </div>
      </div>

      {/* ── Connection banner ── */}
      {wsStatus !== "open" && (
        <div style={{ gridColumn:"1/-1", background:"var(--warn-soft)", borderBottom:"1px solid color-mix(in oklch, var(--warn) 30%, transparent)", padding:"6px 14px", display:"flex", alignItems:"center", gap:8, fontSize:11, color:"var(--warn)", fontFamily:"var(--font-mono)" }}>
          <span style={{ width:7, height:7, borderRadius:"50%", background:"var(--warn)", animation:"pulse 1.6s infinite" }}/>
          {wsStatus === "connecting" ? "Reconnecting to live feed…" : "Live feed disconnected. Data may be stale."}
        </div>
      )}

      {/* ── Mobile nav drawer backdrop ── */}
      {navMenuOpen && <div className="nav-drawer-backdrop" onClick={() => setNavMenuOpen(false)} role="presentation"/>}

      {/* ── Sidebar (slides in as a drawer on mobile) ── */}
      <div ref={sidebarRef} className={`sidebar${navMenuOpen ? " open" : ""}`} aria-modal="true">
        <div className="nav-drawer-head">
          <span>Menu</span>
          <button className="iconbtn" aria-label="Close menu" onClick={() => setNavMenuOpen(false)}><Icon name="x" size={14}/></button>
        </div>
        <div className="nav-label">Workspace</div>
        <div className={`nav-item ${nav==="feed"?"active":""}`} onClick={() => setNav("feed")} onKeyDown={onKeyActivate(() => setNav("feed"))} role="button" tabIndex={0}>
          <Icon name="feed" size={15}/>
          <span>Live signals</span>
          <span className="dot-live"/>
          <span className="count">{filteredSignals.length}</span>
        </div>
        <div className={`nav-item ${nav==="history"?"active":""}`} onClick={() => setNav("history")} onKeyDown={onKeyActivate(() => setNav("history"))} role="button" tabIndex={0}>
          <Icon name="history" size={15}/>
          <span>History</span>
        </div>
        <div className={`nav-item ${nav==="backtest"?"active":""}`} onClick={() => setNav("backtest")} onKeyDown={onKeyActivate(() => setNav("backtest"))} role="button" tabIndex={0}>
          <Icon name="chart" size={15}/>
          <span>Backtest</span>
        </div>

        <div className={`nav-item ${nav==="watchlist"?"active":""}`} onClick={() => setNav("watchlist")} onKeyDown={onKeyActivate(() => setNav("watchlist"))} role="button" tabIndex={0}>
          <Icon name="star" size={15}/>
          <span>Watchlist</span>
          <span className="count">{/* filled on load */}</span>
        </div>
        <div className={`nav-item ${nav==="paper"?"active":""}`} onClick={() => setNav("paper")} onKeyDown={onKeyActivate(() => setNav("paper"))} role="button" tabIndex={0}>
          <Icon name="chart" size={15}/>
          <span>Paper Portfolio</span>
        </div>

        <div className="nav-label">Market</div>
        <div className={`nav-item ${nav==="overview"?"active":""}`} onClick={() => setNav("overview")} onKeyDown={onKeyActivate(() => setNav("overview"))} role="button" tabIndex={0}>
          <Icon name="chart" size={15}/>
          <span>Market overview</span>
        </div>
        <div className={`nav-item ${nav==="sectors"?"active":""}`} onClick={() => setNav("sectors")} onKeyDown={onKeyActivate(() => setNav("sectors"))} role="button" tabIndex={0}>
          <Icon name="sectors" size={15}/>
          <span>Sector heatmap</span>
        </div>
        <div className={`nav-item ${nav==="calendar"?"active":""}`} onClick={() => setNav("calendar")} onKeyDown={onKeyActivate(() => setNav("calendar"))} role="button" tabIndex={0}>
          <Icon name="clock" size={15}/>
          <span>Economic calendar</span>
        </div>

        <div className="nav-label">Configure</div>
        <div className={`nav-item ${nav==="rules"?"active":""}`} onClick={() => setNav("rules")} onKeyDown={onKeyActivate(() => setNav("rules"))} role="button" tabIndex={0}>
          <Icon name="rules" size={15}/>
          <span>Rules &amp; filters</span>
        </div>
        <div className={`nav-item ${nav==="alerts"?"active":""}`} onClick={() => setNav("alerts")} onKeyDown={onKeyActivate(() => setNav("alerts"))} role="button" tabIndex={0}>
          <Icon name="bell" size={15}/>
          <span>Alert rules</span>
          {/* per-ticker alert count badge rendered when rules exist */}
        </div>
        <div className={`nav-item ${nav==="screener"?"active":""}`} onClick={() => setNav("screener")} onKeyDown={onKeyActivate(() => setNav("screener"))} role="button" tabIndex={0}>
          <Icon name="filter" size={15}/>
          <span>Screener</span>
        </div>
        <div className="nav-item" style={{ gap:6, cursor:"default" }}>
          <Icon name="slider" size={15}/>
          <span style={{ flex:1 }}>Threshold</span>
          <div style={{ display:"flex", alignItems:"center", gap:4 }} onClick={e => e.stopPropagation()}>
            <button
              onClick={() => setTweak({ customConf: Math.max(0, threshold - 5) })}
              style={{ width:18, height:18, border:"1px solid var(--line)", borderRadius:3,
                background:"var(--bg-card)", color:"var(--text)", cursor:"pointer",
                fontSize:12, lineHeight:1, display:"grid", placeItems:"center", flexShrink:0 }}>−</button>
            <span className="count mono" style={{ minWidth:32, textAlign:"center" }}>{threshold}%</span>
            <button
              onClick={() => setTweak({ customConf: Math.min(100, threshold + 5) })}
              style={{ width:18, height:18, border:"1px solid var(--line)", borderRadius:3,
                background:"var(--bg-card)", color:"var(--text)", cursor:"pointer",
                fontSize:12, lineHeight:1, display:"grid", placeItems:"center", flexShrink:0 }}>+</button>
          </div>
        </div>

        <div className="nav-label">Account</div>
        <div className="nav-item" onClick={() => setAccountOpen(true)} onKeyDown={onKeyActivate(() => setAccountOpen(true))} role="button" tabIndex={0}>
          <Icon name="user" size={15}/>
          <span>{currentUser.full_name || currentUser.email?.split("@")[0] || "Account"}</span>
          <span style={{ fontSize:9, fontFamily:"var(--font-mono)", fontWeight:700, color:TIER_COLORS[currentUser.subscription_tier], background:TIER_COLORS[currentUser.subscription_tier]+"22", padding:"2px 6px", borderRadius:10 }}>
            {(currentUser.subscription_tier||"FREE").toUpperCase()}{currentUser.is_owner?" ★":""}
          </span>
        </div>
        <div className={`nav-item ${nav==="performance"?"active":""}`} onClick={() => setNav("performance")} onKeyDown={onKeyActivate(() => setNav("performance"))} role="button" tabIndex={0}>
          <Icon name="trending-up" size={15}/>
          <span>My Performance</span>
        </div>
        {(!hasTierAccess(currentUser.subscription_tier,"basic",currentUser.is_owner)) && (
          <div className="nav-item" onClick={() => { setPricingContext("Unlock Telegram delivery, backtesting, paper trading, and more."); setPricingOpen(true); }} onKeyDown={onKeyActivate(() => { setPricingContext("Unlock Telegram delivery, backtesting, paper trading, and more."); setPricingOpen(true); })} style={{ color:"var(--accent)" }} role="button" tabIndex={0}>
            <Icon name="lock" size={15}/>
            <span>Upgrade plan</span>
          </div>
        )}

        {/* ── Market Intelligence panel ── */}
        {marketCtx && (() => {
          const fg      = marketCtx.fear_greed;
          const macro   = marketCtx.macro   || {};
          const breadth = marketCtx.breadth || {};
          const cot     = marketCtx.cot     || {};
          const naaim   = marketCtx.aaii    || {};
          const pc      = marketCtx.put_call || {};
          const rot     = macro.sector_rotation || {};
          const fgClr   = fg ? (fg.score < 30 ? "var(--up)" : fg.score > 70 ? "var(--down)" : "var(--warn)") : "var(--text-faint)";
          const mktRow  = (label, val, color, tipKey) => val != null ? (
            <div key={label} style={{ display:"flex", justifyContent:"space-between", padding:"3px 0", borderBottom:"1px solid var(--line)", fontSize:10, alignItems:"center" }}>
              <span style={{ color:"var(--text-faint)", display:"flex", alignItems:"center", gap:2 }}>
                {label}
                {tipKey && <Tip term={tipKey} iconOnly/>}
              </span>
              <span style={{ fontFamily:"var(--font-mono)", color: color || "var(--text)", fontWeight:500 }}>{val}</span>
            </div>
          ) : null;
          return (
            <div style={{ margin:"8px 12px 4px", background:"var(--bg-card)", border:"1px solid var(--line)", borderRadius:8, padding:"8px 10px" }}>
              <div style={{ fontSize:9, fontFamily:"var(--font-mono)", letterSpacing:"0.1em", color:"var(--text-faint)", textTransform:"uppercase", marginBottom:6 }}>Market Intelligence</div>
              {fg && mktRow("Fear & Greed", `${fg.score?.toFixed(0)} · ${fg.label}`, fgClr, "SENTIMENT")}
              {mktRow("VIX / VIX3M", macro.vix ? `${macro.vix?.toFixed(1)} / ${macro.vix3m?.toFixed(1)||"—"}` : null, macro.vix > 25 ? "var(--down)" : macro.vix < 15 ? "var(--up)" : "var(--warn)", "VIX")}
              {mktRow("Yield Curve", macro.yc_spread != null ? `${macro.yc_spread > 0 ? "+" : ""}${macro.yc_spread?.toFixed(2)}% (2Y-10Y)` : null, macro.yc_spread < 0 ? "var(--down)" : "var(--up)", "YIELD CURVE")}
              {mktRow("Market Breadth", breadth.pct_above_200d != null ? `${breadth.pct_above_200d?.toFixed(0)}% above 200d` : null, breadth.signal === "bullish" ? "var(--up)" : breadth.signal === "bearish" ? "var(--down)" : "var(--warn)", "MARKET BREADTH")}
              {pc.ratio && mktRow("CBOE P/C Ratio", `${pc.ratio?.toFixed(2)} · ${pc.signal}`, pc.signal === "bullish" ? "var(--up)" : pc.signal === "bearish" ? "var(--down)" : "var(--text-faint)", "CBOE P/C")}
              {naaim.exposure != null && mktRow("NAAIM Exposure", `${naaim.exposure?.toFixed(0)}%`, naaim.signal === "bullish" ? "var(--up)" : naaim.signal === "bearish" ? "var(--down)" : "var(--text-faint)", "NAAIM")}
              {cot.net_pct != null && mktRow("COT Lev. Funds", `${cot.net_pct > 0 ? "+" : ""}${cot.net_pct?.toFixed(0)}% net`, cot.signal === "bullish" ? "var(--up)" : cot.signal === "bearish" ? "var(--down)" : "var(--text-faint)", "COT")}
              {macro.dxy_1m != null && mktRow("DXY 1M chg", `${macro.dxy_1m > 0 ? "+" : ""}${macro.dxy_1m?.toFixed(1)}%`, macro.dxy_1m < -2 ? "var(--up)" : macro.dxy_1m > 2 ? "var(--down)" : "var(--text-faint)", "DXY")}
              {macro.cu_gold_1m != null && mktRow("Copper/Gold 1M", `${macro.cu_gold_1m > 0 ? "+" : ""}${macro.cu_gold_1m?.toFixed(1)}%`, macro.cu_gold_1m > 3 ? "var(--up)" : macro.cu_gold_1m < -3 ? "var(--down)" : "var(--text-faint)", "CU/GOLD")}
              {rot.stage && mktRow("Cycle Stage", rot.stage?.charAt(0).toUpperCase() + rot.stage?.slice(1) + (rot.favoured?.length ? ` · ${rot.favoured.slice(0,2).join(", ")}` : ""), "var(--accent)", "CYCLE STAGE")}
              {/* HMM Regime row */}
              {marketCtx.hmm_regime && (() => {
                const hmm = marketCtx.hmm_regime;
                const label = hmm.regime;
                const prob  = label === "bull" ? hmm.bull_prob : label === "bear" ? hmm.bear_prob : Math.max(hmm.bull_prob, hmm.bear_prob);
                const color = label === "bull" ? "var(--up)" : label === "bear" ? "var(--down)" : "var(--warn)";
                const val   = `${label?.toUpperCase()} ${(prob*100).toFixed(0)}% · risk ${(hmm.transition_risk*100).toFixed(0)}%`;
                return mktRow("HMM Regime", val, color, null);
              })()}
            </div>
          );
        })()}

        <div className="sidebar-footer">
          <div className="tier-badge">
            <span className="tb-label">PLAN</span>
            <span className="tb-tier" style={{ color: TIER_COLORS[currentUser.subscription_tier] || "var(--accent)" }}>
              {currentUser.is_owner ? "★ " : ""}{(currentUser.subscription_tier||"FREE").toUpperCase()}
            </span>
          </div>
          <div className="status-card" style={{ marginTop:8 }}>
            <span className="dot-live" style={{ background: online ? "var(--up)" : "var(--warn)" }}/>
            <div style={{ minWidth:0 }}>
              <div className="mono" style={{ fontSize:11 }}>{online ? "Engine running" : "Backend offline"}</div>
              <div className="faint mono" style={{ fontSize:10 }}>{signals.length} signals · {online?"live":"mock"}</div>
              {marketCtx?.api_usage && (
                <div style={{ marginTop:4 }}>
                  <div className="faint mono" style={{ fontSize:9 }}>Finnhub {marketCtx.api_usage.used_last_60s}/{marketCtx.api_usage.limit}/min</div>
                  <div style={{ height:2, background:"var(--line)", borderRadius:1, overflow:"hidden", marginTop:2 }}>
                    <div style={{ height:"100%", borderRadius:1, width:`${marketCtx.api_usage.pct||0}%`, background: (marketCtx.api_usage.pct||0) > 80 ? "var(--down)" : "var(--up)" }}/>
                  </div>
                </div>
              )}
              {/* TSYS-11b: last-refresh + stale-data indicator (live-ticks via `now`) */}
              {(() => {
                if (!lastRefresh) return null;
                const ageS = Math.max(0, Math.round((now - lastRefresh) / 1000));
                const stale = ageS > 120;
                const ageLabel = ageS < 60 ? `${ageS}s` : `${Math.round(ageS / 60)}m`;
                return (
                  <div className="faint mono" style={{ fontSize: 9, marginTop: 4, color: stale ? "var(--warn)" : undefined }}>
                    {stale ? "⚠ stale · " : ""}updated {ageLabel} ago
                  </div>
                );
              })()}
              <VersionBadge/>
            </div>
          </div>
        </div>
      </div>

      {/* ── Main ── */}
      <div className="main" ref={mainRef} id="main-content">
        {/* Feed pane */}
        <div className="pane">
          {/* Slim ad banner for free-tier users — above the feed header */}
          <AdSlot user={currentUser} slim={true}/>
          <SignalQuotaBanner quota={signalQuota} user={currentUser}/>
          <div className="pane-head">
            <span className="title">Signal feed</span>
            <span className="sep"/>
            <span className="chip">Today · {filteredSignals.length}</span>
            {!whatsNewSeen && signals.length > 0 && (
              <span className="whats-new" onClick={() => setWhatsNewSeen(true)} onKeyDown={onKeyActivate(() => setWhatsNewSeen(true))} title="Click to dismiss" role="button" tabIndex={0}>
                <span className="wn-pulse"/>
                <strong>{signals.length} live</strong>
                <span className="faint">· click to dismiss</span>
              </span>
            )}
          </div>
          <FilterChips
            filter={feedFilter}
            setFilter={setFeedFilter}
            counts={{
              all:   signals.filter(s => (s.confidence||0) >= threshold && (!s.style || s.style===styleFilter)).length,
              buy:   signals.filter(s => (s.confidence||0) >= threshold && s.action==="BUY"  && (!s.style || s.style===styleFilter)).length,
              sell:  signals.filter(s => (s.confidence||0) >= threshold && s.action==="SELL" && (!s.style || s.style===styleFilter)).length,
              high:  signals.filter(s => (s.confidence||0) >= 75 && (!s.style || s.style===styleFilter)).length,
            }}
          />
          <div className="style-strip">
            <span className="ss-label">STYLE</span>
            <div className="ss-seg">
              {["intraday","swing","position"].map(s => (
                <button key={s} className={`ss-btn ${tweakState.style===s?"on":""}`}
                  onClick={() => { setTweak({ style:s }); setFeedFilter("all"); }}
                  title={STYLE_INFO[s].hold}>
                  {STYLE_INFO[s].label}
                </button>
              ))}
            </div>
            <span className="ss-meta mono">
              <span className="faint">HORIZON</span> {STYLE_INFO[tweakState.style]?.horizon||"—"}
              <span className="dot"/>
              <span className="faint">WINDOW</span> {tweakState.startTime}–{tweakState.endTime}
            </span>
            <span className="ss-days">
              {["Mon","Tue","Wed","Thu","Fri"].map(d => (
                <span key={d} className={`day ${tweakState.days?.includes(d)?"on":""}`} onClick={() => {
                  const cur = tweakState.days || [];
                  setTweak({ days: cur.includes(d) ? cur.filter(x => x !== d) : [...cur, d] });
                }} onKeyDown={onKeyActivate(() => { const cur = tweakState.days || []; setTweak({ days: cur.includes(d) ? cur.filter(x => x !== d) : [...cur, d] }); })} role="button" tabIndex={0}>{d[0]}</span>
              ))}
            </span>
          </div>
          <div className="help-strip">
            <span className="k"><span className="k-dot" style={{ background:"var(--up)" }}/><Tip term="BUY">BUY</Tip></span>
            <span className="k"><span className="k-dot" style={{ background:"var(--down)" }}/><Tip term="SELL">SELL</Tip></span>
            <span className="k"><span className="k-dot" style={{ background:"var(--warn)" }}/><Tip term="HOLD">HOLD</Tip></span>
            <span style={{ marginLeft:"auto" }}>Tap to expand</span>
          </div>
          {ptrState !== "idle" && (
            <div style={{ textAlign:"center", padding:"8px 0", color:"var(--text-faint)", fontSize:11, fontFamily:"var(--font-mono)", borderBottom:"1px solid var(--line)" }}>
              {ptrState === "released" ? "Release to refresh…" : "Pull to refresh…"}
            </div>
          )}
          <div className="feed" ref={feedRef}
            onTouchStart={e => {
              if (feedRef.current && feedRef.current.scrollTop === 0) {
                ptrStartY.current = e.touches[0].clientY;
              }
            }}
            onTouchMove={e => {
              if (ptrStartY.current === 0) return;
              const y = e.touches[0].clientY;
              const diff = y - ptrStartY.current;
              if (diff > 0 && feedRef.current && feedRef.current.scrollTop === 0) {
                setPtrState(diff > 80 ? "released" : "pulling");
                if (diff > 120) ptrStartY.current = y - 120;
              }
            }}
            onTouchEnd={() => {
              if (ptrState === "released") {
                setRefreshing(true);
                loadData(false).finally(() => setRefreshing(false));
              }
              setPtrState("idle");
              ptrStartY.current = 0;
            }}>
            {loading && <div style={{ padding:"40px 0", textAlign:"center", color:"var(--text-faint)", fontSize:12 }}>Connecting to backend…</div>}
            {!loading && filteredSignals.length === 0 && (
              <div style={{ padding:"44px 24px", textAlign:"center", color:"var(--text-dim)", fontSize:12, maxWidth:340, margin:"0 auto" }}>
                <div style={{ fontSize:30, marginBottom:10, opacity:0.35 }}>◎</div>
                <div style={{ marginBottom:6, color:"var(--text)", fontWeight:600, fontSize:13 }}>No signals above {threshold}% confidence</div>
                <div style={{ fontSize:12, color:"var(--text-faint)", lineHeight:1.55, marginBottom:14 }}>
                  The market is quiet for your current filters. The next scan runs automatically in {countdown}s — or widen your search below.
                </div>
                <div style={{ display:"flex", gap:8, justifyContent:"center", flexWrap:"wrap" }}>
                  {threshold > 40 && (
                    <button className="btn" style={{ fontSize:11, padding:"6px 14px" }}
                      onClick={() => setTweak({ customConf: Math.max(40, threshold - 10) })}>
                      Lower to {Math.max(40, threshold - 10)}%
                    </button>
                  )}
                  {feedFilter !== "all" && (
                    <button className="btn" style={{ fontSize:11, padding:"6px 14px" }}
                      onClick={() => setFeedFilter("all")}>
                      Clear filter
                    </button>
                  )}
                  <button className="btn ghost" style={{ fontSize:11, padding:"6px 14px" }} onClick={manualScan}>
                    Scan now
                  </button>
                </div>
              </div>
            )}
            {visibleSignals.map((s, idx) => (
              <React.Fragment key={s.id}>
                <SignalRow s={s}
                  active={s.id === activeId}
                  expanded={s.id === expandedId}
                  onToggle={() => { setActiveId(s.id); setExpandedId(expandedId === s.id ? null : s.id); }}
                  onOpen={() => setActiveId(s.id)}
                  onFullDetail={() => {
                    setActiveId(s.id);
                    setDetailTab("simulate");
                    if (window.innerWidth <= 768) {
                      setTimeout(() => scrollToPanel(1), 0);
                    }
                  }}
                  onSend={() => sendToTelegram(s.id)}
                  onSkip={() => skipSignal(s.id)}
                  outcomeByTicker={outcomeByTicker}
                  allSignals={signals}
                />
                {/* Ad slot shown every 5th signal in the feed */}
                {(idx + 1) % 5 === 0 && <AdSlot user={currentUser}/>}
              </React.Fragment>
            ))}
            {hiddenCount > 0 && (
              <button
                onClick={() => setFeedLimit(l => l + 20)}
                style={{ width:"100%", padding:"10px 0", background:"var(--bg-2)",
                         border:"none", borderTop:"1px solid var(--line)",
                         color:"var(--text-dim)", fontFamily:"var(--font-mono)",
                         fontSize:11, cursor:"pointer", letterSpacing:"0.08em" }}>
                Show {Math.min(hiddenCount, 20)} more · {hiddenCount} remaining
              </button>
            )}
            {suppressedSignals.length > 0 && (
              <>
                <div style={{ padding:"10px 14px", fontFamily:"var(--font-mono)", fontSize:10, color:"var(--text-faint)", textTransform:"uppercase", letterSpacing:"0.1em", borderBottom:"1px solid var(--line)", background:"var(--bg-1)" }}>
                  Suppressed · below {threshold}% · {suppressedSignals.length}
                </div>
                {visibleSuppressed.map(s => (
                  <SignalRow key={s.id} s={s} suppressed active={false} expanded={false}
                    onToggle={() => {}} onOpen={() => {}} onSend={() => {}} onSkip={() => {}}/>
                ))}
                {hiddenSuppressed > 0 && (
                  <button
                    onClick={() => setSuppressedLimit(l => l + SUPPRESSED_PAGE)}
                    style={{ width:"100%", padding:"9px 0", background:"var(--bg-2)",
                             border:"none", borderTop:"1px solid var(--line)",
                             color:"var(--text-faint)", fontFamily:"var(--font-mono)",
                             fontSize:10, cursor:"pointer", letterSpacing:"0.08em" }}>
                    Show {Math.min(hiddenSuppressed, SUPPRESSED_PAGE)} more suppressed · {hiddenSuppressed} remaining
                  </button>
                )}
              </>
            )}
          </div>
        </div>

        {/* Detail pane */}
        {active && (
          <div className="pane">
            <div className="pane-head">
              <span className="title">Recommendation</span>
              <span className="sep"/>
              <span className="mono faint" style={{ fontSize:10 }}>
                {fmtETFull(active.ts, etAbbr)}
              </span>
              <div className="right">
                {active.style && <span className={`style-badge ${active.style}`}>{active.style}</span>}
                <span className={`chip ${up?"up":"down"}`}>{sgn(active.change||0)}{fmt(active.changePct||0)}%</span>
                <span className="chip">R:R {active.rr||"—"}</span>
              </div>
            </div>
            <div className="detail">
              <div className="detail-hero">
                <div className="detail-row">
                  <div className={`rec-action-big ${active.action}`}><Tip term={active.action}>{active.action}</Tip></div>
                  <div style={{ minWidth:0 }}>
                    <div className="detail-ticker">{active.ticker}</div>
                    <div className="detail-company">{active.company}</div>
                  </div>
                  <div style={{ marginLeft:"auto", textAlign:"right" }}>
                    {/* Live WebSocket price — updates in real time from tick messages */}
                    {livePrice && livePrice !== active.price ? (
                      <>
                        <div className="detail-price mono" style={{ fontSize:18 }}>${fmt(livePrice)}</div>
                        <div style={{ fontSize:9, fontFamily:"var(--font-mono)", color:"var(--text-faint)" }}>
                          Live · at signal <span style={{ color:"var(--text-dim)" }}>${fmt(active.price)}</span>
                          {active.stop && (
                            <span style={{ marginLeft:6, color: livePrice <= active.stop ? "var(--down)" : "var(--text-faint)" }}>
                              {livePrice <= active.stop ? "⚠ BELOW STOP" : `${((livePrice - active.stop) / active.stop * 100).toFixed(1)}% above stop`}
                            </span>
                          )}
                        </div>
                      </>
                    ) : (
                      <>
                        <div className="detail-price mono">${fmt(active.price)}</div>
                        <div className={`detail-change mono ${up?"up":"down"}`}>{sgn(active.change||0)}{fmt(active.change||0)} ({sgn(active.changePct||0)}{fmt(active.changePct||0)}%)</div>
                      </>
                    )}
                  </div>
                </div>
                <div className="hero-meta">
                  <span className="mono" style={{ display:"flex", alignItems:"center", gap:6, flexShrink:0 }}>
                    <span className="faint"><Tip term="CONFIDENCE">CONF</Tip></span>
                    <strong style={{ color:
                      (active.confidence||0) >= 75 ? "var(--up)"
                      : (active.confidence||0) >= 62 ? "var(--accent)"
                      : (active.confidence||0) >= 50 ? "var(--warn)"
                      : "var(--down)"
                    }}>{(active.confidence||0).toFixed(0)}%</strong>
                    <div title={`Confidence: ${(active.confidence||0).toFixed(0)}%`}
                      style={{ width:56, height:5, borderRadius:2.5, background:"var(--bg-3)", overflow:"hidden" }}>
                      <div style={{
                        height:"100%", borderRadius:2.5,
                        width:`${active.confidence||0}%`,
                        background: (active.confidence||0) >= 75 ? "var(--up)"
                                  : (active.confidence||0) >= 62 ? "var(--accent)"
                                  : (active.confidence||0) >= 50 ? "var(--warn)"
                                  : "var(--down)",
                      }}/>
                    </div>
                    {active.confidence_warning && (
                      <span className="calib-badge" title="Confidence significantly exceeds historical win rate">⚠ CALIB</span>
                    )}
                  </span>
                  <ConfidenceTrend ticker={active.ticker} current={active.confidence||65}/>
                  <span className="mono"><span className="faint"><Tip term="R:R">R:R</Tip></span> <strong>{active.rr||"—"}</strong></span>
                  <span className="mono"><span className="faint"><Tip term="SENTIMENT">SENT</Tip></span> <strong style={{ color:(active.sentiment||0) > 0.2 ? "var(--up)" : (active.sentiment||0) < -0.2 ? "var(--down)" : "var(--warn)" }}>{sgn(active.sentiment||0)}{fmt(active.sentiment||0,2)}</strong></span>
                  <span className="mono faint" style={{ marginLeft:"auto" }}>{(active.sources||[]).join(" · ")}</span>
                </div>
                {(active.sources||[]).length >= 3 && (
                  <div className="cluster-chip">
                    <span className="cc-dot"/>
                    <strong>SIGNAL CLUSTER</strong> · {(active.sources||[]).length} independent sources agree · ×{(1 + (active.sources||[]).length * 0.04).toFixed(2)} boost
                  </div>
                )}
                <div className="hero-headline">{active.headline}</div>
              </div>

              <div className="plain-english" style={{ flexDirection:"column", gap:10 }}>
                <div style={{ display:"flex", alignItems:"flex-start", gap:10 }}>
                  <div className="ico">i</div>
                  <div style={{ flex:1 }}>
                    <div style={{ display:"flex", alignItems:"center", gap:8, marginBottom:6, flexWrap:"wrap" }}>
                      <strong style={{ color:"var(--text)" }}>What this means</strong>
                      {(active.plain_english?.tf_short || active.style) && (
                        <span style={{ fontSize:10, fontFamily:"var(--font-mono)", fontWeight:700,
                          padding:"2px 8px", borderRadius:10, background:"color-mix(in oklch,var(--accent) 15%,transparent)",
                          color:"var(--accent)", textTransform:"uppercase", letterSpacing:"0.08em" }}>
                          ⏱ {active.plain_english?.tf_short || active.style}
                        </span>
                      )}
                    </div>
                    <div style={{ fontSize:13, lineHeight:1.65, color:"var(--text-dim)" }}>
                      {active.plain_english?.summary || (
                        <>
                          {ACTION_SUBTITLE[active.action]}. The system is <strong>{(active.confidence||0).toFixed(0)}%</strong> confident based on {(active.rationale||[]).length || "multiple"} signals.{" "}
                          {active.entry ? <>Entry near <strong>${fmt(active.entry)}</strong>, stop <strong>${fmt(active.stop)}</strong>, target <strong>${fmt(active.target)}</strong>.</> : "No trade plan yet."}
                        </>
                      )}
                    </div>
                    {active.plain_english?.top_reasons?.length > 0 && (
                      <div style={{ marginTop:8, display:"flex", flexDirection:"column", gap:3 }}>
                        {active.plain_english.top_reasons.slice(0,2).map((r, i) => (
                          <div key={i} style={{ fontSize:11, color:"var(--text-faint)", display:"flex", gap:6, alignItems:"flex-start" }}>
                            <span style={{ color:"var(--accent)", flexShrink:0, marginTop:1 }}>→</span>
                            <span>{r}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
                {active.entry && (
                  <div style={{ display:"flex", gap:6, flexWrap:"wrap", paddingLeft:34 }}>
                    <span style={{ fontSize:11, color:"var(--text-faint)" }}>
                      Entry <strong style={{ color:"var(--text)" }}>${fmt(active.entry)}</strong>
                      {" · "}Stop <strong style={{ color:"var(--down)" }}>${fmt(active.stop)}</strong>
                      {" · "}Target <strong style={{ color:"var(--up)" }}>${fmt(active.target)}</strong>
                      {" · "}Risk <strong>${fmt(Math.abs((active.entry||0)-(active.stop||0)),0)}</strong>/share to make <strong>${fmt(Math.abs((active.target||0)-(active.entry||0)),0)}</strong>
                    </span>
                  </div>
                )}
              </div>

              {/* ── Detail pane tab strip ── */}
              <div className="detail-tabs">
                {[["why","Why"],["position","Position"],["simulate","Simulate"],["similar","Similar"]].map(([id,lbl]) => (
                  <button key={id} className={`detail-tab${detailTab===id?" active":""}`}
                    onClick={() => setDetailTab(id)}>{lbl}</button>
                ))}
              </div>

              {/* ── Tab: Why (chart + rationale + predictive) ── */}
              {detailTab === "why" && <>
                {/* Chart with entry/stop/target lines — first thing traders look at */}
                <div className="chart-wrap">
                  <div className="chart-head">
                    <span className="mono" style={{ fontSize:10, color:"var(--text-faint)", textTransform:"uppercase", letterSpacing:"0.1em" }}>
                      {active.ticker} · {chartPeriod}
                    </span>
                    <span style={{ display:"flex", gap:10, alignItems:"center", fontSize:9, fontFamily:"var(--font-mono)", color:"var(--text-faint)" }}>
                      {active.entry  && <span style={{ color:"var(--text-dim)" }}>— ENTRY</span>}
                      {active.stop   && <span style={{ color:"var(--down)" }}>— STOP</span>}
                      {active.target && <span style={{ color:"var(--up)" }}>— TARGET</span>}
                    </span>
                    <div className="tabs" style={{ marginLeft:"auto" }}>
                      {["1D","5D","1M","3M","1Y"].map(t => (
                        <span key={t} className={`tab ${t===chartPeriod?"active":""}`}
                          onClick={() => setChartPeriod(t)} onKeyDown={onKeyActivate(() => setChartPeriod(t))} style={{ cursor:"pointer" }} role="button" tabIndex={0}>{t}</span>
                      ))}
                    </div>
                  </div>
                  <Chart signal={active} style={tweakState.chartStyle} period={chartPeriod}/>
                  {/* ── Compare vs benchmark ─────────────────────────────────── */}
                  <div style={{ display:"flex", alignItems:"center", gap:6, marginTop:8, paddingTop:8, borderTop:"1px solid var(--line)" }}>
                    <span style={{ fontSize:9, fontFamily:"var(--font-mono)", color:"var(--text-faint)", textTransform:"uppercase", letterSpacing:"0.1em", flexShrink:0 }}>Compare vs</span>
                    {["SPY","QQQ","IWM","GLD"].map(b => (
                      <button key={b} onClick={() => setCompareVs(compareVs === b ? null : b)}
                        style={{ fontSize:9, fontFamily:"var(--font-mono)", padding:"2px 8px", borderRadius:4, cursor:"pointer",
                          border: compareVs === b ? "1px solid var(--accent)" : "1px solid var(--line)",
                          background: compareVs === b ? "var(--accent)22" : "var(--bg-2)",
                          color: compareVs === b ? "var(--accent)" : "var(--text-faint)", transition:"all 0.15s" }}>
                        {b}
                      </button>
                    ))}
                    {compareVs && (
                      <button onClick={() => setCompareVs(null)}
                        style={{ fontSize:9, marginLeft:"auto", background:"none", border:"none", color:"var(--text-faint)", cursor:"pointer", padding:"2px 4px" }}>
                        ✕ Clear
                      </button>
                    )}
                  </div>
                  {compareVs && active?.ticker && (
                    <CompareChart ticker={active.ticker} versus={compareVs} period={chartPeriod}/>
                  )}
                </div>
                <WhyNow signal={active}/>
                {(predictive || active.confidence) && (
                  <PredictiveIntervals signal={active} predictive={predictive}/>
                )}
              </>}

              {/* ── Tab: Position (sizing calculator) ── */}
              {detailTab === "position" && active.entry && active.stop && (
                !hasTierAccess(currentUser.subscription_tier, "basic", currentUser.is_owner) ? (
                  <div style={{ margin:"20px", padding:"14px", background:"var(--warn-soft)", border:"1px solid color-mix(in oklch, var(--warn) 30%, transparent)", borderRadius:8, fontSize:12, color:"var(--warn)", display:"flex", alignItems:"center", gap:8 }}>
                    <span style={{ width:7, height:7, borderRadius:"50%", background:"var(--warn)" }}/>
                    Position sizing and paper trading require Basic or higher.
                    <button className="btn primary" style={{ marginLeft:"auto", fontSize:11, padding:"5px 12px" }} onClick={() => { setPricingContext("Position sizing and paper trading require Basic or higher."); setPricingOpen(true); }}>Upgrade</button>
                  </div>
                ) : (
                <PositionCalc signal={active} onPaperTrade={() => {
                  authFetch("/api/paper/orders", {
                    method:"POST",
                    headers:{"Content-Type":"application/json"},
                    body:JSON.stringify({ symbol:active.ticker, qty:1,
                      side: active.action === "BUY" ? "buy" : "sell",
                      type:"market", time_in_force:"day" }),
                  }).catch(()=>{});
                }}/>
              ))}

              {/* ── Tab: Simulate (Monte Carlo) ── */}
              {detailTab === "simulate" && (
                <SimulatedReturnsPanel signal={active} onClose={() => setDetailTab("why")}/>
              )}

              {/* ── Tab: Similar setups ── */}
              {detailTab === "similar" && (
                <SimilarSignals signal={active} allSignals={histSignals}/>
              )}

              {/* ── Probability of Success panel ── */}
              {(predLoading || predictive) && (
                <div className="section" style={{ marginTop:0 }}>
                  <div className="section-title" style={{ display:"flex", alignItems:"center", gap:8 }}>
                    <Tip term="P(SUCCESS)">Probability of Success</Tip>
                    {predLoading && <span style={{ fontSize:10, color:"var(--text-faint)", fontWeight:400 }}>calculating…</span>}
                    {predictive && !predLoading && (
                      <span style={{ fontSize:10, color:"var(--text-faint)", fontWeight:400, marginLeft:"auto" }}>
                        {predictive.message}
                      </span>
                    )}
                  </div>

                  {predictive && !predLoading && (() => {
                    const cp   = predictive.composite_p;
                    const pct  = cp != null ? Math.round(cp * 100) : null;
                    const clr  = pct == null ? "var(--text-faint)"
                                : pct >= 65 ? "var(--up)"
                                : pct >= 45 ? "var(--warn)"
                                : "var(--down)";
                    const iconMap = { bullish:"▲", bearish:"▼", neutral:"–" };
                    const iconClr = { bullish:"var(--up)", bearish:"var(--down)", neutral:"var(--text-faint)" };

                    return (
                      <>
                        {/* ── Composite gauge + horizon table ── */}
                        <div style={{ display:"flex", gap:16, alignItems:"flex-start", marginBottom:12, flexWrap:"wrap" }}>

                          {/* Gauge */}
                          <div style={{ display:"flex", flexDirection:"column", alignItems:"center", minWidth:90 }}>
                            <div style={{ fontSize:32, fontWeight:800, color:clr, fontFamily:"var(--font-mono)", lineHeight:1 }}>
                              {pct != null ? `${pct}%` : "—"}
                            </div>
                            <div style={{ fontSize:10, color:"var(--text-faint)", marginTop:4, textAlign:"center" }}>
                              composite P(success)
                            </div>
                            {pct != null && (
                              <div style={{ width:80, height:6, background:"var(--bg-3)", borderRadius:3, marginTop:8, overflow:"hidden" }}>
                                <div style={{ width:`${pct}%`, height:"100%", background:clr, borderRadius:3, transition:"width 0.6s" }}/>
                              </div>
                            )}
                          </div>

                          {/* Horizon breakdown */}
                          {predictive.horizons.length > 0 && (
                            <div style={{ flex:1, minWidth:180 }}>
                              <table style={{ width:"100%", borderCollapse:"collapse", fontSize:11 }}>
                                <thead>
                                  <tr style={{ color:"var(--text-faint)" }}>
                                    <th style={{ textAlign:"left",  padding:"3px 6px", fontWeight:500 }}><Tip term="1D">Hold</Tip></th>
                                    <th style={{ textAlign:"right", padding:"3px 6px", fontWeight:500 }}><Tip term="P(SUCCESS)">P(win)</Tip></th>
                                    <th style={{ textAlign:"right", padding:"3px 6px", fontWeight:500 }}>Avg return</th>
                                    <th style={{ textAlign:"right", padding:"3px 6px", fontWeight:500 }}><Tip term="P10">P10</Tip></th>
                                    <th style={{ textAlign:"right", padding:"3px 6px", fontWeight:500 }}><Tip term="P90">P90</Tip></th>
                                    <th style={{ textAlign:"right", padding:"3px 6px", fontWeight:500 }} title="Number of similar historical signals used">n</th>
                                  </tr>
                                </thead>
                                <tbody>
                                  {predictive.horizons.map(h => {
                                    const hclr = h.p_success >= 0.65 ? "var(--up)" : h.p_success < 0.45 ? "var(--down)" : "var(--warn)";
                                    return (
                                      <tr key={h.horizon} style={{ borderTop:"1px solid var(--line)" }}>
                                        <td style={{ padding:"4px 6px", color:"var(--text-faint)", fontFamily:"var(--font-mono)" }}>{h.horizon}</td>
                                        <td style={{ padding:"4px 6px", textAlign:"right", color:hclr, fontWeight:600, fontFamily:"var(--font-mono)" }}>{Math.round(h.p_success*100)}%</td>
                                        <td style={{ padding:"4px 6px", textAlign:"right", color:(h.expected||0)>0?"var(--up)":"var(--down)", fontFamily:"var(--font-mono)" }}>{h.expected!=null?`${h.expected>0?"+":""}${h.expected.toFixed(1)}%`:"—"}</td>
                                        <td style={{ padding:"4px 6px", textAlign:"right", color:"var(--text-faint)", fontFamily:"var(--font-mono)", fontSize:10 }}>{h.ci_10!=null?`${h.ci_10>0?"+":""}${h.ci_10.toFixed(1)}%`:"—"}</td>
                                        <td style={{ padding:"4px 6px", textAlign:"right", color:"var(--text-faint)", fontFamily:"var(--font-mono)", fontSize:10 }}>{h.ci_90!=null?`${h.ci_90>0?"+":""}${h.ci_90.toFixed(1)}%`:"—"}</td>
                                        <td style={{ padding:"4px 6px", textAlign:"right", color:"var(--text-faint)", fontSize:10 }}>{h.n}</td>
                                      </tr>
                                    );
                                  })}
                                </tbody>
                              </table>
                            </div>
                          )}
                        </div>

                        {/* ── Plain-English summary ── */}
                        {predictive.summary && (
                          <div style={{ background:"var(--bg-2)", border:"1px solid var(--line)", borderRadius:8, padding:"10px 14px", marginBottom:12, fontSize:12, color:"var(--text)", lineHeight:1.6 }}>
                            {predictive.summary}
                          </div>
                        )}

                        {/* ── Insight cards ── */}
                        {(predictive.insights || []).length > 0 && (
                          <div style={{ display:"flex", flexDirection:"column", gap:6 }}>
{predictive.insights.map((ins, i) => (
                              <div key={i} style={{
                                display:"flex", gap:10, alignItems:"flex-start",
                                background:"var(--bg-2)", border:"1px solid var(--line)",
                                borderLeft:`3px solid ${iconClr[ins.icon]||"var(--line)"}`,
                                borderRadius:6, padding:"8px 12px", fontSize:11,
                              }}>
                                <span style={{ color:iconClr[ins.icon]||"var(--text-faint)", fontSize:13, flexShrink:0, marginTop:1 }}>
                                  {iconMap[ins.icon]||"–"}
                                </span>
                                <div>
                                  <div style={{ fontWeight:600, marginBottom:2, fontSize:11 }}>{ins.head}</div>
                                  <div style={{ color:"var(--text-faint)", lineHeight:1.5 }}>{ins.body}</div>
                                  {ins.path && ins.path.length > 0 && (
                                    <div style={{ marginTop: 8, height: 24, width: 120 }}>
                                      <PathSparkline path={ins.path} />
                                    </div>
                                  )}
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </>
                    );
                  })()}

                  {predLoading && (
                    <div style={{ padding:"20px 0", textAlign:"center", color:"var(--text-faint)", fontSize:12 }}>
                      Analysing {active?.n_similar || ""} historical signals…
                    </div>
                  )}
                </div>
              )}

              <div className="chart-wrap">
                <div className="chart-head">
                  <span className="mono" style={{ fontSize:10, color:"var(--text-faint)", textTransform:"uppercase", letterSpacing:"0.1em" }}>
                    {active.ticker} · {chartPeriod}
                  </span>
                  {/* Legend */}
                  <span style={{ display:"flex", gap:10, alignItems:"center", fontSize:9, fontFamily:"var(--font-mono)", color:"var(--text-faint)" }}>
                    <span style={{ color:"var(--accent)" }}>— SMA</span>
                    {active.entry && <span style={{ color:"var(--text-dim)" }}>- - ENTRY</span>}
                    {active.stop   && <span style={{ color:"var(--down)" }}>- - STOP</span>}
                    {active.target && <span style={{ color:"var(--up)" }}>- - TARGET</span>}
                  </span>
                  <div className="tabs" style={{ marginLeft:"auto" }}>
                    {["1D","5D","1M","3M","1Y"].map(t => (
                      <span key={t} className={`tab ${t===chartPeriod?"active":""}`} onClick={() => setChartPeriod(t)} onKeyDown={onKeyActivate(() => setChartPeriod(t))} style={{ cursor:"pointer" }} role="button" tabIndex={0}>{t}</span>
                    ))}
                  </div>
                </div>
                <Chart signal={active} style={tweakState.chartStyle} period={chartPeriod}/>
                {(active.rationale||[]).length > 0 && (
                <div className="section">
                  <div className="section-title">
                    Why this recommendation · {active.rationale.length} signals agree
                    <InfoPop title="Signal Sources Explained">
                      <strong>TA</strong> = Technical Analysis (RSI, MACD, Bollinger etc.)<br/>
                      <strong>Options</strong> = Unusual options activity & sweeps<br/>
                      <strong>13F</strong> = SEC institutional 13F filings (hedge fund moves)<br/>
                      <strong>Insider</strong> = SEC Form 4 insider buying/selling<br/>
                      <strong>Analyst</strong> = Consensus price targets & ratings<br/>
                      <strong>Fundamentals</strong> = Piotroski F-Score, FCF yield, ROE<br/>
                      <strong>Macro</strong> = VIX, yield curve, credit spreads, DXY<br/>
                      <strong>Market Sentiment</strong> = F&G, NAAIM, CBOE P/C, COT<br/>
                      <strong>Social</strong> = StockTwits & Reddit WSB<br/>
                      Each source contributes independently — more agreement = higher confidence.
                    </InfoPop>
                  </div>
                  <div className="rationale-list">
                    {active.rationale.map((r, i) => (
                      <div key={i} className="rationale-item">
                        <div className="src" title={r.src}>{srcAbbr(r.src)}</div>
                        <div>
                          <h2>{tipifyHead(r.head)}</h2>
                          <p>{r.body}</p>
                          <div className="meta">
                            <span className={`sentiment chip ${r.sentiment==="pos"?"up":r.sentiment==="neg"?"down":"warn"}`}>{r.sentiment?.toUpperCase()}</span>
                            {r.meta}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {active.entry && (
                <div className="section">
                  <div className="section-title">
                    Trade plan
                    <InfoPop title="How to read the trade plan">
                      <strong>Entry</strong>: Open your position near this price.<br/>
                      <strong>Stop-Loss</strong>: Exit immediately if price hits this — caps your max loss to roughly 2× ATR (average daily range).<br/>
                      <strong>Target</strong>: Your planned exit if the trade works — set at 3× the risk amount.<br/>
                      <strong>R:R</strong>: Risk-to-Reward. A ratio of 1.5 means you risk $1 to potentially make $1.50.<br/><br/>
                      <em>Always use a stop-loss. Position size so the stop-loss loss = ≤1-2% of your portfolio.</em>
                    </InfoPop>
                  </div>
                  <div className="rr-grid">
                    <div className="rr-card">
                      <div className="lbl"><Tip term="ENTRY">Buy at (Entry)</Tip></div>
                      <div className="v">${fmt(active.entry)}</div>
                      <div className="d">Current ${fmt(active.price)}</div>
                    </div>
                    <div className="rr-card">
                      <div className="lbl"><Tip term="STOP">Cut loss (Stop)</Tip></div>
                      <div className="v down">${fmt(active.stop)}</div>
                      <div className="d">You'd lose {fmt(Math.abs((active.entry-(active.stop||0))/(active.entry||1))*100)}%</div>
                    </div>
                    <div className="rr-card">
                      <div className="lbl"><Tip term="TARGET">Take profit (Target)</Tip></div>
                      <div className="v up">${fmt(active.target)}</div>
                      <div className="d">You'd gain {fmt(Math.abs(((active.target||0)-active.entry)/active.entry)*100)}%</div>
                    </div>
                  </div>
                  <div className="rr-bar">
                    <div className="track">
                      {(() => {
                        const lo = Math.min(active.stop||0, active.target||0);
                        const hi = Math.max(active.stop||0, active.target||0);
                        const entryPct = hi > lo ? ((active.entry - lo) / (hi - lo)) * 100 : 50;
                        const isBuy = active.action === "BUY";
                        return (
                          <>
                            <div className="fill-loss" style={{ width:`${isBuy?entryPct:100-entryPct}%` }}/>
                            <div className="fill-gain" style={{ width:`${isBuy?100-entryPct:entryPct}%`, position:"absolute", right:0, top:0, bottom:0, borderRadius:"0 4px 4px 0" }}/>
                            <div className="marker" style={{ left:`calc(${entryPct}% - 1px)` }}/>
                          </>
                        );
                      })()}
                    </div>
                    <div className="rr-labels">
                      <span>STOP ${fmt(Math.min(active.stop||0,active.target||0))}</span>
                      <span>ENTRY ${fmt(active.entry)}</span>
                      <span>TGT ${fmt(Math.max(active.stop||0,active.target||0))}</span>
                    </div>
                  </div>
                </div>
              )}

              {/* ── Journal note ── */}
              {active?.id && <NoteEditor signal={active} onSave={saveNote} onDirty={d => { hasUnsavedData.current = d; }}/>}

              <div className="action-row">
                <button className="btn primary" onClick={() => sendToTelegram(active.id)}>
                  <Icon name="telegram" size={14}/> Send to Telegram
                </button>
                <button className="btn" onClick={() => skipSignal(active.id)}>
                  <Icon name="clock" size={14}/> Skip
                </button>
                <button className="btn" onClick={() => setAlertOpen(true)}>
                  <Icon name="bell" size={14}/> Alert
                </button>
                {hasTierAccess(currentUser.subscription_tier, "basic", currentUser.is_owner) && active.action !== "HOLD" && (
                  <button
                    className="btn"
                    style={{ background: paperTradeFlash ? "var(--up)" : undefined, color: paperTradeFlash ? "#fff" : undefined, transition:"all 0.2s" }}
                    onClick={() => {
                      if (paperSubmitting) return;
                      setPaperSubmitting(true);
                      const side = active.action === "BUY" ? "buy" : "sell";
                      authFetch("/api/paper/orders", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ symbol: active.ticker, qty: 1, side, type: "market", time_in_force: "day" }),
                      }).then(res => {
                        if (res && res.ok) {
                          setPaperTradeFlash(true);
                          setTimeout(() => setPaperTradeFlash(false), 1500);
                        }
                      }).finally(() => setPaperSubmitting(false));
                    }}
                    disabled={paperSubmitting}
                    title="Paper Trade (P)">
                    {paperSubmitting ? "Placing…" : paperTradeFlash ? "✓ Placed" : "Paper Trade"}
                  </button>
                )}
                <button
                  className="btn ghost"
                  style={{ marginLeft:"auto", color: active.reviewed ? "var(--up)" : undefined }}
                  onClick={() => reviewSignal(active.id)}
                  title={active.reviewed ? "Already reviewed" : "Mark as reviewed"}>
                  {active.reviewed ? "✓ Reviewed" : "Mark reviewed"}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Delivery pane — SimulatedReturnsPanel now lives in the detail tab strip;
            this pane always shows the Telegram delivery log */}
        <TelegramPane log={log} online={online} onOpenAccount={() => setAccountOpen(true)}/>

        {/* Overlays */}
        <WatchlistView open={nav==="watchlist"} onClose={() => setNav("feed")}
          quotes={tickerTape} histSignals={histSignals}/>
        <RulesView open={nav==="rules"} onClose={() => setNav("feed")} aggr={tweakState.aggressiveness} style={tweakState.style} days={tweakState.days} startTime={tweakState.startTime} endTime={tweakState.endTime} setTweak={setTweak} customConf={tweakState.customConf}/>
        <MarketOverviewView open={nav==="overview"} onClose={() => setNav("feed")} online={online}/>
        <SectorView open={nav==="sectors"} onClose={() => setNav("feed")}/>
        <CalendarView open={nav==="calendar"} onClose={() => setNav("feed")}/>
        <PaperView open={nav==="paper"} onClose={() => setNav("feed")} online={online}/>
        <HistoryView open={nav==="history"} onClose={() => setNav("feed")} online={online}/>
        <MyPerformanceView open={nav==="performance"} onClose={() => setNav("feed")}/>
        <AlertsView open={nav==="alerts"} onClose={() => setNav("feed")}/>
        <ScreenerView open={nav==="screener"} onClose={() => setNav("feed")}/>
        <BacktestView open={nav==="backtest"} onClose={() => setNav("feed")} online={online}
          btCache={btCacheRef.current}
          onBtCache={onBtCache}/>
        <PricingView open={pricingOpen} onClose={() => setPricingOpen(false)} user={currentUser} context={pricingContext}/>
        <AccountModal open={accountOpen} onClose={() => setAccountOpen(false)} user={currentUser} setUser={setCurrentUser} onUpgrade={() => { setAccountOpen(false); setPricingContext("Choose a plan to unlock live signals and delivery."); setPricingOpen(true); }} onDirty={d => { hasUnsavedData.current = d; }}/>
        <PriceAlertModal open={alertOpen} onClose={() => setAlertOpen(false)} ticker={active?.ticker} currentPrice={active?.price}/>

        {/* Mobile delivery-log overlay */}
        <div ref={deliveryRef} className={`overlay ${nav==="delivery"?"open":""}`} aria-modal="true">
          <TelegramPane log={log} online={online} onOpenAccount={() => setAccountOpen(true)} onClose={() => setNav("feed")}/>
        </div>
      </div>

      {/* ── Mobile panel pager (hidden on desktop) ── */}
      <div className="mobile-pager" aria-label="Panel navigation">
        <button
          className="pager-arrow"
          aria-label="Previous panel"
          disabled={panelIdx <= 0}
          onClick={() => scrollToPanel(panelIdx - 1)}>
          {'‹'}
        </button>
        <div className="pager-dots" aria-hidden="true">
          {Array.from({ length: panelCount }).map((_, i) => (
            <span key={i} className={`pager-dot${i === panelIdx ? ' active' : ''}`}/>
          ))}
        </div>
        <button
          className="pager-arrow"
          aria-label="Next panel"
          disabled={panelIdx >= panelCount - 1}
          onClick={() => scrollToPanel(panelIdx + 1)}>
          {'›'}
        </button>
      </div>

      {/* ── Mobile bottom navigation bar (hidden on desktop via CSS) ── */}
      <div className="mobile-nav">
        {[
          ["feed","feed","Feed"],
          ["history","clock","History"],
          ["backtest","bar-chart","Backtest"],
          ["watchlist","eye","Watchlist"],
          ["delivery","send","Delivery"],
          ["overview","globe","Market"],
          ["sectors","sectors","Sectors"],
          ["calendar","clock","Calendar"],
          ["rules","rules","Rules"],
          ["paper","chart","Paper"],
          ["performance","bar-chart","Perf"],
          ["screener","filter","Screen"],
          ["alerts","bell","Alerts"],
        ].map(([id, icon, label]) => (
          <div key={id} className={`mobile-nav-item${nav===id?" active":""}`} onClick={() => setNav(id)} onKeyDown={onKeyActivate(() => setNav(id))} role="button" tabIndex={0}>
            <Icon name={icon} size={18}/>
            <span>{label}</span>
          </div>
        ))}
      </div>

      {/* ── Status bar ── */}
      <div className="statusbar">
        <span><span className="dot"/>CONNECTED</span>
        <span>SIGNALS <span className="mono">{filteredSignals.length}</span></span>
        <span style={{ display:"flex", alignItems:"center", gap:3, userSelect:"none" }}>
          THRESH{" "}
          <button onClick={() => setTweak({ customConf: Math.max(0, threshold - 5) })}
            style={{ background:"none", border:"none", color:"var(--text-faint)", cursor:"pointer",
              fontSize:10, padding:"0 1px", lineHeight:1 }}>−</button>
          <span className="mono">{threshold}%</span>
          <button onClick={() => setTweak({ customConf: Math.min(100, threshold + 5) })}
            style={{ background:"none", border:"none", color:"var(--text-faint)", cursor:"pointer",
              fontSize:10, padding:"0 1px", lineHeight:1 }}>+</button>
        </span>
        {marketCtx?.macro?.vix != null && <span>VIX <span className="mono">{marketCtx.macro.vix.toFixed(2)}</span></span>}
        {marketCtx?.macro?.yield_10y != null && <span>10Y <span className="mono">{marketCtx.macro.yield_10y.toFixed(2)}%</span></span>}
        {marketCtx?.macro?.spx_1m != null && <span>SPX <span className="mono" style={{ color: marketCtx.macro.spx_1m>=0?"var(--up)":"var(--down)" }}>{marketCtx.macro.spx_1m>=0?"+":""}{marketCtx.macro.spx_1m.toFixed(1)}%</span></span>}
        <span>SENT <span className="mono">{log.filter(l=>l.status==="sent").length}</span> TODAY</span>
        <span style={{ marginLeft:"auto" }}>MODE · {(tweakState.aggressiveness||"balanced").toUpperCase()}</span>
        <span title={`Your local time: ${localClock} (${localTz})`}>{etOffset} {etAbbr}</span>
      </div>

      {/* ── Disclaimer footer ── */}
      <div className="disclaimer-bar" style={{ gridColumn:"1/-1", background:"var(--bg-1)", borderTop:"1px solid var(--line)", padding:"5px 20px", display:"flex", alignItems:"center", gap:10, fontSize:10, color:"var(--text-faint)", fontFamily:"var(--font-mono)" }}>
        <svg aria-hidden="true" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="var(--warn)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink:0 }}>
          <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
          <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
        </svg>
        <span style={{ fontWeight:600, color:"var(--warn)", letterSpacing:"0.06em" }}>NOT FINANCIAL ADVICE</span>
        <span style={{ color:"var(--line)" }}>·</span>
        <span>For informational & educational purposes only · Past performance does not guarantee future results · All trading involves risk of loss</span>
        <span style={{ marginLeft:"auto", display:"flex", gap:12 }}>
          <a href="/tos" target="_blank" style={{ color:"var(--text-faint)" }}>ToS</a>
          <a href="/privacy" target="_blank" style={{ color:"var(--text-faint)" }}>Privacy</a>
        </span>
      </div>

      <TweaksPanel open={tweaksOpen} onClose={() => setTweaksOpen(false)} state={tweakState} set={setTweak} saveError={tweakSaveError}/>
      <HotkeyHelp open={hkOpen} onClose={() => setHkOpen(false)} onTour={() => setTourOpen(true)}/>
      <DemoTour open={tourOpen} onClose={() => { try { localStorage.setItem(TOUR_KEY, "1"); } catch {} setTourOpen(false); }}/>
    </div>
  );
}

/* ─── FE-4: Error boundary — catches unhandled render errors ─────────────── */
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  componentDidCatch(error, info) {
    console.error("[ErrorBoundary]", error, info.componentStack);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          display:"flex", flexDirection:"column", alignItems:"center",
          justifyContent:"center", minHeight:"100vh", gap:"1rem",
          background:"var(--bg-0)", color:"var(--text)", fontFamily:"monospace",
          padding:"2rem", textAlign:"center",
        }}>
          <div style={{fontSize:"2rem"}}>⚠</div>
          <div style={{fontSize:"1.2rem", fontWeight:600}}>Something went wrong</div>
          <div style={{color:"var(--text-dim)", maxWidth:"480px", fontSize:"0.875rem"}}>
            {this.state.error?.message || "An unexpected error occurred."}
          </div>
          <button
            onClick={() => { this.setState({ hasError:false, error:null }); window.location.reload(); }}
            style={{
              marginTop:"1rem", padding:"0.5rem 1.5rem",
              background:"var(--accent)", color:"#000", border:"none",
              borderRadius:"6px", cursor:"pointer", fontSize:"0.9rem",
            }}
          >Reload</button>
        </div>
      );
    }
    return this.props.children;
  }
}

/* ─── Accessibility audit (dev only) ──────────────────────────────────────── */
if (location.hostname === 'localhost' || location.hostname === '127.0.0.1') {
  import('@axe-core/react').then(axe => {
    axe.default(React, ReactDOM, 1000);
  }).catch(() => {});
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <ErrorBoundary>
    <App/>
  </ErrorBoundary>
);
