/* ─── UI constants and helpers ──────────────────────────────────────────────── */
const ACTION_SUBTITLE = {
  BUY:  "Price likely to rise — consider buying",
  SELL: "Price likely to fall — consider selling",
  HOLD: "No clear edge — skip for now",
};

const fmt = (n, d = 2) => Number(n).toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d });
const pct = n => `${n >= 0 ? "+" : ""}${fmt(n, 2)}%`;
const sgn = n => n >= 0 ? "+" : "";

/* TSYS-11c: explainability badge — shows the policy / model / calibration versions
   behind current signals so a change in recommendations is traceable. Self-contained
   (own fetch of the public version-info endpoint); renders nothing until loaded. */
function VersionBadge() {
  const [v, setV] = useState(null);
  useEffect(() => {
    let alive = true;
    fetch("/api/public/version-info")
      .then(r => (r.ok ? r.json() : null))
      .then(d => { if (alive && d) setV(d); })
      .catch(() => {});
    return () => { alive = false; };
  }, []);
  if (!v || !v.policy_version) return null;
  const cal = v.calibration_version ? String(v.calibration_version).slice(0, 10) : "—";
  const title = `Policy ${v.policy_version} · Model ${v.model_trained_at || "—"} · Calibration ${v.calibration_version || "—"}`;
  return (
    <div className="faint mono" style={{ fontSize: 9, marginTop: 4 }} title={title}>
      v {v.policy_version} · cal {cal}
    </div>
  );
}

const Icon = ({ name, size = 16 }) => {
  const paths = {
    search:  <><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></>,
    bell:    <><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10 21a2 2 0 0 0 4 0"/></>,
    settings:<><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></>,
    send:    <path d="m22 2-7 20-4-9-9-4Z"/>,
    x:       <><path d="m18 6-12 12"/><path d="m6 6 12 12"/></>,
    "arrow-left": <><path d="M19 12H5"/><path d="m12 19-7-7 7-7"/></>,
    feed:    <><path d="M4 11a9 9 0 0 1 9 9"/><path d="M4 4a16 16 0 0 1 16 16"/><circle cx="5" cy="19" r="1"/></>,
    chart:   <><path d="M3 3v18h18"/><path d="m7 14 4-4 4 4 5-5"/></>,
    chat:    <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>,
    plug:    <><path d="M9 2v6"/><path d="M15 2v6"/><path d="M6 8h12v4a6 6 0 0 1-12 0z"/><path d="M12 18v4"/></>,
    rules:   <><path d="M14 2v6h6"/><path d="M4 13.5V4a2 2 0 0 1 2-2h8l6 6v4"/><path d="m16 16 2 2 4-4"/><path d="M10 18H4a2 2 0 0 1-2-2v0a2 2 0 0 1 2-2h6"/></>,
    history: <><path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/><path d="M12 7v5l3 2"/></>,
    slider:  <><line x1="21" y1="4" x2="14" y2="4"/><line x1="10" y1="4" x2="3" y2="4"/><line x1="21" y1="12" x2="12" y2="12"/><line x1="8" y1="12" x2="3" y2="12"/><line x1="21" y1="20" x2="16" y2="20"/><line x1="12" y1="20" x2="3" y2="20"/><line x1="14" y1="2" x2="14" y2="6"/><line x1="8" y1="10" x2="8" y2="14"/><line x1="16" y1="18" x2="16" y2="22"/></>,
    plus:    <><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></>,
    clock:   <><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></>,
    refresh: <><path d="M21 12a9 9 0 1 1-3-6.7"/><path d="M21 4v5h-5"/></>,
    user:    <><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></>,
    lock:    <><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></>,
    telegram:<path d="M22 2L11 13M22 2L15 22l-4-9-9-4 20-7z"/>,
    sectors: <><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></>,
    star:    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>,
    filter:  <><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></>,
    "bar-chart": <><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/></>,
    eye:     <><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></>,
    globe:   <><circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></>,
  };
  return (
    <svg aria-hidden="true" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      {paths[name]}
    </svg>
  );
};

/* ── Portal tooltip — renders at document.body so it's never clipped ── */
function Tip({ term, children, iconOnly = false }) {
  const def = GLOSSARY[term?.toUpperCase?.()] || GLOSSARY[term];
  const [pos, setPos]         = React.useState(null);
  const [visible, setVisible] = React.useState(false);
  const ref = React.useRef(null);

  if (!def) return <>{children ?? (iconOnly ? null : term)}</>;

  const TIP_W = 280;
  const TIP_H = 130;

  const show = () => {
    const el = ref.current;
    if (!el) return;
    const r  = el.getBoundingClientRect();
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    const idealX = r.left + r.width / 2;
    const x = Math.max(TIP_W / 2 + 8, Math.min(idealX, vw - TIP_W / 2 - 8));
    const canFitAbove = r.top > TIP_H + 16;
    const y     = canFitAbove ? r.top - 8 : r.bottom + 8;
    const below = !canFitAbove;
    setPos({ x, y, below });
    setVisible(true);
  };
  const hide = () => setVisible(false);

  const portal = visible && pos && ReactDOM.createPortal(
    <div style={{
      position:"fixed",
      left: pos.x,
      top:  pos.y,
      transform: pos.below ? "translateX(-50%)" : "translate(-50%, -100%)",
      background:"#1c2333", border:"1px solid rgba(255,255,255,0.14)",
      borderRadius:8, padding:"10px 14px", fontSize:11, color:"#e2e8f0",
      width: TIP_W, lineHeight:1.65, zIndex:99999, pointerEvents:"none",
      boxShadow:"0 8px 32px rgba(0,0,0,0.6)",
      whiteSpace:"normal", wordBreak:"break-word",
    }}>
      <strong style={{ color:"var(--accent)", display:"block", marginBottom:4,
        textTransform:"uppercase", letterSpacing:"0.08em", fontSize:9 }}>
        {term}
      </strong>
      {def}
    </div>,
    document.body
  );

  return (
    <>
      <span
        ref={ref}
        onMouseEnter={show}
        onMouseLeave={hide}
        style={{ display:"inline-flex", alignItems:"center", gap:2, cursor:"help" }}>
        {!iconOnly && (children ?? term)}
        <svg aria-hidden="true" width="10" height="10" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
          style={{ color:"rgba(255,255,255,0.35)", flexShrink:0, marginTop:1 }}>
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="8"/>
          <polyline points="11 12 12 12 12 16 13 16"/>
        </svg>
      </span>
      {portal}
    </>
  );
}

/* ── InfoPop: clickable ⓘ — portal panel so sidebar can't clip it ─────────── */
function InfoPop({ title, children }) {
  const [open, setOpen]   = React.useState(false);
  const [pos, setPos]     = React.useState(null);
  const ref               = React.useRef(null);

  const POP_W = 340;

  const toggle = () => {
    if (!open && ref.current) {
      const r  = ref.current.getBoundingClientRect();
      const vw = window.innerWidth;
      const vh = window.innerHeight;
      const x = Math.max(8, Math.min(r.left, vw - POP_W - 8));
      const canFitBelow = r.bottom + 200 < vh;
      const y = canFitBelow ? r.bottom + 6 : r.top - 6;
      setPos({ x, y, above: !canFitBelow });
    }
    setOpen(o => !o);
  };

  const portal = open && pos && ReactDOM.createPortal(
    <>
      <div onClick={() => setOpen(false)}
        style={{ position:"fixed", inset:0, zIndex:99997, background:"transparent" }}/>
      <div style={{
        position:"fixed", left:pos.x,
        top:       pos.above ? undefined : pos.y,
        bottom:    pos.above ? (window.innerHeight - pos.y + 6) : undefined,
        width: POP_W,
        background:"#1c2333", border:"1px solid color-mix(in oklch, var(--accent) 40%, transparent)",
        borderRadius:10, padding:"14px 18px", fontSize:12,
        color:"#e2e8f0", lineHeight:1.7, zIndex:99998,
        boxShadow:"0 12px 48px rgba(0,0,0,0.7)",
      }} onClick={e => e.stopPropagation()}>
        <strong style={{ color:"var(--accent)", display:"block", marginBottom:8,
          textTransform:"uppercase", letterSpacing:"0.08em", fontSize:10 }}>
          {title}
        </strong>
        {children}
        <button onClick={() => setOpen(false)}
          style={{ display:"block", marginTop:12, fontSize:10, color:"rgba(255,255,255,0.4)",
            background:"none", border:"none", cursor:"pointer", padding:0 }}>
          × Close
        </button>
      </div>
    </>,
    document.body
  );

  return (
    <>
      <button ref={ref} onClick={toggle}
        style={{ background:"none", border:"none", cursor:"pointer",
          color:"rgba(255,255,255,0.4)", padding:"0 2px", lineHeight:1,
          fontSize:12, display:"inline-flex", alignItems:"center" }}
        title={`About: ${title}`}
        aria-label={`Info about ${title}`}>
        ⓘ
      </button>
      {portal}
    </>
  );
}

/* ─── Interactive OHLCV Chart (LightweightCharts v4) ────────────────────────── */
const PERIOD_API = { "1D": "1d", "5D": "5d", "1M": "1mo", "3M": "3mo", "1Y": "1y" };

// ── Drawing tools helpers ─────────────────────────────────────────────────────
const _DRAW_KEY = ticker => `chart_drawings_v1_${ticker}`;

function _loadDrawings(ticker) {
  try { return JSON.parse(localStorage.getItem(_DRAW_KEY(ticker)) || "[]"); }
  catch { return []; }
}
function _saveDrawings(ticker, prices) {
  try { localStorage.setItem(_DRAW_KEY(ticker), JSON.stringify(prices)); }
  catch {}
}

function Chart({ signal, style, period = "3M" }) {
  const containerRef = useRef(null);
  const chartRef     = useRef(null);
  const priceSeriesRef = useRef(null);
  const priceLinesRef  = useRef([]);   // [{price, lineObj}]
  const [ohlcv,        setOhlcv]       = useState(null);
  const [loading,      setLoading]     = useState(true);
  const [error,        setError]       = useState(false);
  const [needsUpgrade, setNeedsUpgrade] = useState(false);
  const [drawMode,    setDrawMode]    = useState(false);
  const [lineCount,   setLineCount]   = useState(0);  // triggers re-render on change

  useEffect(() => {
    if (!signal?.ticker) return;
    setLoading(true); setError(false); setNeedsUpgrade(false);
    const ctrl = new AbortController();
    const apiPeriod = PERIOD_API[period] || "3mo";
    authFetch(`/api/chart/${encodeURIComponent(signal.ticker)}?period=${apiPeriod}`, { signal: ctrl.signal })
      .then(async res => {
        if (res.status === 402) { setNeedsUpgrade(true); return; }
        if (!res.ok) { setError(true); return; }
        const d = await res.json();
        if (Array.isArray(d) && d.length > 0) setOhlcv(d); else setError(true);
      })
      .catch(() => setError(true))
      .finally(() => setLoading(false));
    return () => ctrl.abort();
  }, [signal?.ticker, period]);

  useEffect(() => {
    const LC = window.LightweightCharts;
    if (!containerRef.current || !ohlcv || !LC) return;

    const cs      = getComputedStyle(document.documentElement);
    const resolve = v => cs.getPropertyValue(v).trim() || null;
    const C = {
      bg:      resolve("--bg")         || "#0d0d0d",
      surface: resolve("--bg-1")       || "#141414",
      line:    resolve("--line")       || "#222",
      faint:   resolve("--text-faint") || "#555",
      dim:     resolve("--text-dim")   || "#888",
      text:    resolve("--text")       || "#e5e5e5",
      up:      resolve("--up")     || "#22d3ee",
      down:    resolve("--down")   || "#fb4d6d",
      accent:  resolve("--accent") || "#22d3ee",
    };

    if (chartRef.current) { chartRef.current.remove(); chartRef.current = null; }

    const el      = containerRef.current;
    const isIntra = period === "1D" || period === "5D";

    const chart = LC.createChart(el, {
      width:  el.clientWidth,
      height: 300,
      layout: {
        background: { color: "transparent" },
        textColor:  C.faint,
        fontSize:   10,
      },
      grid: {
        vertLines: { color: C.line, style: 1 },
        horzLines: { color: C.line, style: 1 },
      },
      rightPriceScale: { borderColor: C.line },
      timeScale: {
        borderColor:   C.line,
        timeVisible:   isIntra,
        secondsVisible: false,
        fixLeftEdge:   true,
        fixRightEdge:  true,
      },
      crosshair: { mode: 0 },
    });

    const toTime = d =>
      isIntra ? Math.floor(new Date(d.date.replace(" ", "T") + "Z").getTime() / 1000)
              : d.date.split(" ")[0];

    const timed = ohlcv.map(d => ({ ...d, _t: toTime(d) })).filter(d => d._t);

    let priceSeries;
    if (style === "candles") {
      priceSeries = chart.addCandlestickSeries({
        upColor:        C.up,   downColor:        C.down,
        borderUpColor:  C.up,   borderDownColor:  C.down,
        wickUpColor:    C.up,   wickDownColor:    C.down,
      });
      priceSeries.setData(timed.map(d => ({
        time: d._t, open: d.open, high: d.high, low: d.low, close: d.close,
      })));
    } else {
      const lineColor = (signal.change || 0) >= 0 ? C.up : C.down;
      priceSeries = chart.addAreaSeries({
        lineColor,
        topColor:    lineColor + "33",
        bottomColor: "transparent",
        lineWidth:   style === "area" ? 1.5 : 1.5,
      });
      priceSeries.setData(timed.map(d => ({ time: d._t, value: d.close })));
    }

    const window200 = Math.min(200, timed.length - 1);
    if (timed.length >= 20) {
      const smaData = [];
      for (let i = 19; i < timed.length; i++) {
        const w = Math.min(window200, i + 1);
        const avg = timed.slice(i + 1 - w, i + 1).reduce((s, d) => s + d.close, 0) / w;
        smaData.push({ time: timed[i]._t, value: +avg.toFixed(2) });
      }
      const smaSeries = chart.addLineSeries({
        color: C.accent, lineWidth: 1, lineStyle: 1,
        priceLineVisible: false, lastValueVisible: true,
        title: `${window200 >= 200 ? "200" : window200}-DMA`,
      });
      smaSeries.setData(smaData);
    }

    const addLine = (price, color, title) => {
      if (!price) return;
      priceSeries.createPriceLine({ price, color, lineWidth: 1, lineStyle: 2, title, axisLabelVisible: true });
    };
    addLine(signal.entry,  C.dim,  "ENTRY");
    addLine(signal.stop,   C.down, "STOP");
    addLine(signal.target, C.up,   "TARGET");

    const volSeries = chart.addHistogramSeries({
      color:       C.accent + "44",
      priceFormat: { type: "volume" },
      priceScaleId: "vol",
      scaleMargins: { top: 0.78, bottom: 0 },
    });
    chart.priceScale("vol").applyOptions({ scaleMargins: { top: 0.78, bottom: 0 } });
    volSeries.setData(timed.map(d => ({
      time:  d._t,
      value: d.volume,
      color: d.close >= d.open ? C.up + "55" : C.down + "55",
    })));

    chart.timeScale().fitContent();
    chartRef.current  = chart;
    // Accessibility: the LightweightCharts canvas wrapper is focusable but has no name.
    el.querySelector('div[role="button"]')?.setAttribute('aria-label', `${signal?.ticker || "Price"} interactive chart`);
    priceSeriesRef.current = priceSeries;
    priceLinesRef.current  = [];

    // Restore saved drawings for this ticker
    const ticker = signal?.ticker || "";
    const savedPrices = _loadDrawings(ticker);
    savedPrices.forEach(price => {
      const lineObj = priceSeries.createPriceLine({
        price, color: "#a78bfa", lineWidth: 1, lineStyle: 2,
        axisLabelVisible: true, title: "─",
      });
      priceLinesRef.current.push({ price, lineObj });
    });
    setLineCount(savedPrices.length);

    const ro = new ResizeObserver(() => {
      if (chartRef.current) chartRef.current.applyOptions({ width: el.clientWidth });
    });
    ro.observe(el);
    return () => {
      ro.disconnect();
      if (chartRef.current) { chartRef.current.remove(); chartRef.current = null; }
      priceSeriesRef.current = null;
      priceLinesRef.current  = [];
    };
  }, [ohlcv, style, period, signal?.entry, signal?.stop, signal?.target, signal?.change]);

  // Drawing tool handlers
  const handleChartClick = e => {
    if (!drawMode || !priceSeriesRef.current || !chartRef.current) return;
    const rect  = e.currentTarget.getBoundingClientRect();
    const y     = e.clientY - rect.top;
    const price = priceSeriesRef.current.coordinateToPrice(y);
    if (price == null) return;
    const rounded = +price.toFixed(2);
    const lineObj = priceSeriesRef.current.createPriceLine({
      price: rounded, color: "#a78bfa", lineWidth: 1, lineStyle: 2,
      axisLabelVisible: true, title: "─",
    });
    const updated = [...priceLinesRef.current, { price: rounded, lineObj }];
    priceLinesRef.current = updated;
    _saveDrawings(signal?.ticker || "", updated.map(l => l.price));
    setLineCount(updated.length);
  };

  const handleChartRightClick = e => {
    e.preventDefault();
    if (!priceSeriesRef.current || priceLinesRef.current.length === 0) return;
    const rect  = e.currentTarget.getBoundingClientRect();
    const y     = e.clientY - rect.top;
    const clickPrice = priceSeriesRef.current.coordinateToPrice(y);
    if (clickPrice == null) return;
    // Remove the price line closest to the right-click y position
    let closest = null, minDist = Infinity;
    priceLinesRef.current.forEach(l => {
      const d = Math.abs(l.price - clickPrice);
      if (d < minDist) { minDist = d; closest = l; }
    });
    if (closest && minDist < Math.abs(clickPrice) * 0.02) {
      priceSeriesRef.current.removePriceLine(closest.lineObj);
      priceLinesRef.current = priceLinesRef.current.filter(l => l !== closest);
      _saveDrawings(signal?.ticker || "", priceLinesRef.current.map(l => l.price));
      setLineCount(priceLinesRef.current.length);
    }
  };

  const clearDrawings = () => {
    if (!priceSeriesRef.current) return;
    priceLinesRef.current.forEach(l => priceSeriesRef.current.removePriceLine(l.lineObj));
    priceLinesRef.current = [];
    _saveDrawings(signal?.ticker || "", []);
    setLineCount(0);
  };

  return (
    <div style={{ position:"relative", width:"100%" }}>
      {/* Drawing toolbar */}
      {!loading && !needsUpgrade && !error && (
        <div style={{ display:"flex", gap:6, marginBottom:4, alignItems:"center" }}>
          <button
            onClick={() => setDrawMode(m => !m)}
            title={drawMode ? "Click chart to place level · Right-click to remove" : "Toggle draw mode"}
            style={{
              padding:"2px 8px", fontSize:10, fontFamily:"var(--font-mono)",
              background: drawMode ? "var(--accent)" : "var(--bg-1)",
              color: drawMode ? "#fff" : "var(--text-dim)",
              border: "1px solid " + (drawMode ? "var(--accent)" : "var(--line)"),
              borderRadius:4, cursor:"pointer", letterSpacing:"0.05em",
            }}>
            {drawMode ? "✏ DRAWING" : "✏ DRAW"}
          </button>
          {lineCount > 0 && (
            <button
              onClick={clearDrawings}
              title="Clear all drawn levels"
              style={{
                padding:"2px 8px", fontSize:10, fontFamily:"var(--font-mono)",
                background:"var(--bg-1)", color:"var(--text-faint)",
                border:"1px solid var(--line)", borderRadius:4, cursor:"pointer",
              }}>
              CLEAR ({lineCount})
            </button>
          )}
          {drawMode && (
            <span style={{ fontSize:10, color:"var(--text-faint)", fontFamily:"var(--font-mono)" }}>
              click = add · right-click = remove
            </span>
          )}
        </div>
      )}
      {loading && (
        <div style={{ position:"absolute", inset:0, display:"grid", placeItems:"center",
          color:"var(--text-faint)", fontSize:11, zIndex:2, pointerEvents:"none" }}>
          Loading chart…
        </div>
      )}
      {needsUpgrade && (
        <div style={{ position:"absolute", inset:0, display:"flex", flexDirection:"column",
          alignItems:"center", justifyContent:"center", gap:10, zIndex:2,
          background:"rgba(17,24,39,0.88)", backdropFilter:"blur(4px)", borderRadius:8 }}>
          <div style={{ fontSize:11, color:"var(--text-dim)", fontFamily:"var(--font-mono)",
                        textTransform:"uppercase", letterSpacing:"0.1em" }}>Chart — Basic+</div>
          <div style={{ fontSize:12, color:"var(--text)", textAlign:"center", lineHeight:1.6, maxWidth:200 }}>
            Interactive OHLCV chart requires a <strong>Basic</strong> subscription.
          </div>
          <a href="/signup?plan=basic" style={{ padding:"6px 16px", background:"var(--accent)",
            color:"#fff", borderRadius:6, fontSize:11, fontWeight:600, textDecoration:"none",
            fontFamily:"var(--font-mono)", letterSpacing:"0.05em" }}>
            Upgrade for $29/mo →
          </a>
        </div>
      )}
      {error && !loading && !needsUpgrade && (
        <div style={{ position:"absolute", inset:0, display:"grid", placeItems:"center",
          color:"var(--text-faint)", fontSize:11, zIndex:2, pointerEvents:"none" }}>
          Chart data unavailable
        </div>
      )}
      <div
        ref={containerRef}
        onClick={handleChartClick}
        onContextMenu={handleChartRightClick}
        style={{
          width:"100%", height:300,
          opacity: loading ? 0.2 : 1, transition:"opacity 0.2s",
          cursor: drawMode ? "crosshair" : "default",
        }}
      />
    </div>
  );
}

/* ─── Multi-Ticker Relative Performance Chart ─────────────────────────────── */
const BENCH_LABELS = { "SPY": "S&P 500", "QQQ": "Nasdaq 100", "IWM": "Russell 2000", "GLD": "Gold" };

function CompareChart({ ticker, versus, period = "3M" }) {
  const containerRef = useRef(null);
  const chartRef     = useRef(null);
  const [data,    setData]    = useState(null);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState(false);

  const apiPeriod = PERIOD_API[period] || "3mo";

  useEffect(() => {
    if (!ticker || !versus) return;
    setLoading(true); setError(false); setData(null);
    const ctrl = new AbortController();
    apiFetch(`/api/chart/${encodeURIComponent(ticker)}/relative?versus=${encodeURIComponent(versus)}&period=${apiPeriod}`, { signal: ctrl.signal })
      .then(d => {
        if (d?.ticker?.length > 1 && d?.bench?.length > 1) setData(d);
        else setError(true);
      })
      .catch(() => setError(true))
      .finally(() => setLoading(false));
    return () => ctrl.abort();
  }, [ticker, versus, apiPeriod]);

  useEffect(() => {
    const LC = window.LightweightCharts;
    if (!containerRef.current || !data || !LC) return;
    if (chartRef.current) { chartRef.current.remove(); chartRef.current = null; }

    const cs      = getComputedStyle(document.documentElement);
    const resolve = v => cs.getPropertyValue(v).trim() || null;
    const C = {
      bg:     resolve("--bg")         || "#0d0d0d",
      line:   resolve("--line")       || "#222",
      faint:  resolve("--text-faint") || "#555",
      accent: resolve("--accent") || "#22d3ee",
      bench:  resolve("--warn")   || "#fbbf24",
    };

    const chart = LC.createChart(containerRef.current, {
      width:  containerRef.current.clientWidth,
      height: 160,
      layout: { background: { color: "transparent" }, textColor: C.faint, fontSize: 10 },
      grid:   { vertLines: { color: C.line, style: 1 }, horzLines: { color: C.line, style: 1 } },
      rightPriceScale: { borderColor: C.line },
      timeScale: { borderColor: C.line, fixLeftEdge: true, fixRightEdge: true },
      crosshair: { mode: 0 },
      localization: { priceFormatter: v => (v >= 0 ? "+" : "") + v.toFixed(1) + "%" },
    });

    const tickerSeries = chart.addLineSeries({ color: C.accent, lineWidth: 2, title: ticker, priceLineVisible: false });
    const benchSeries  = chart.addLineSeries({ color: C.bench,  lineWidth: 1.5, lineStyle: 1, title: versus, priceLineVisible: false });

    tickerSeries.setData(data.ticker.map(d => ({ time: d.date, value: d.value })));
    benchSeries.setData(data.bench.map(d => ({ time: d.date, value: d.value })));

    chart.timeScale().fitContent();
    chartRef.current = chart;
    containerRef.current?.querySelector('div[role="button"]')?.setAttribute('aria-label', `${ticker} vs ${versus} relative performance chart`);

    const ro = new ResizeObserver(() => {
      if (chartRef.current) chartRef.current.applyOptions({ width: containerRef.current.clientWidth });
    });
    ro.observe(containerRef.current);
    return () => { ro.disconnect(); if (chartRef.current) { chartRef.current.remove(); chartRef.current = null; } };
  }, [data, ticker, versus]);

  return (
    <div style={{ marginTop: 6 }}>
      <div style={{ display:"flex", alignItems:"center", gap:12, marginBottom:6, padding:"0 2px" }}>
        <span style={{ fontSize:9, fontFamily:"var(--font-mono)", color:"var(--text-faint)", textTransform:"uppercase", letterSpacing:"0.1em" }}>
          % Return vs {BENCH_LABELS[versus] || versus} · {period}
        </span>
        <span style={{ display:"flex", gap:8, fontSize:9, fontFamily:"var(--font-mono)" }}>
          <span style={{ color:"var(--accent)" }}>— {ticker}</span>
          <span style={{ color:"var(--warn)" }}>— {versus}</span>
        </span>
      </div>
      <div style={{ position:"relative" }}>
        {loading && <div style={{ position:"absolute", inset:0, display:"grid", placeItems:"center", color:"var(--text-faint)", fontSize:11, zIndex:2 }}>Loading comparison…</div>}
        {error && !loading && <div style={{ position:"absolute", inset:0, display:"grid", placeItems:"center", color:"var(--text-faint)", fontSize:11, zIndex:2 }}>Comparison unavailable</div>}
        <div ref={containerRef} style={{ width:"100%", height:160, opacity: loading ? 0.2 : 1, transition:"opacity 0.2s" }}/>
      </div>
    </div>
  );
}

/* ─── AdSlot — shown only to free-tier users ────────────────────────────────
   Replace data-ad-slot with your real Google AdSense slot IDs once the account
   is approved. The component renders nothing for paid subscribers.
   BUG FIX: useEffect moved outside conditional block to comply with React hooks rules. */
function AdSlot({ user, slim = false }) {
  const tier = user?.subscription_tier || "free";
  const isPaid = tier !== "free" || user?.is_owner;
  const hasAdSense = typeof window !== "undefined" && window.adsbygoogle !== undefined;
  const adsense = (typeof window !== "undefined" && window.SIGNAL_ADSENSE) || {};
  const adClient = adsense.client || "";
  const adSlot = slim ? adsense.slimSlot : adsense.rectangleSlot;
  const canRenderAds = hasAdSense && adClient && adSlot;

  // Hook must always be called — conditional logic is inside the effect body
  React.useEffect(() => {
    if (!isPaid && canRenderAds) {
      try { (window.adsbygoogle = window.adsbygoogle || []).push({}); } catch (_) {}
    }
  }, [isPaid, canRenderAds]);

  if (isPaid) return null;

  if (slim) return (
    <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between",
                  padding:"6px 14px", background:"var(--bg-2)", borderBottom:"1px solid var(--line)",
                  fontSize:10, color:"var(--text-faint)", fontFamily:"var(--font-mono)" }}>
      {canRenderAds ? (
        <ins className="adsbygoogle" style={{ display:"inline-block", width:"100%", height:50 }}
             data-ad-client={adClient} data-ad-slot={adSlot} data-ad-format="horizontal"/>
      ) : (
        <div style={{ width:"100%", textAlign:"center", opacity:0.5 }}>
          📢 Ad · <a href="/signup?plan=basic" style={{ color:"var(--accent)", textDecoration:"none" }}>
            Upgrade to Basic ($29/mo)
          </a> to remove ads
        </div>
      )}
    </div>
  );

  return (
    <div style={{ margin:"6px 0", padding:"10px 14px", background:"var(--bg-2)",
                  border:"1px solid var(--line)", borderRadius:8,
                  display:"flex", flexDirection:"column", alignItems:"center", gap:6 }}>
      {canRenderAds ? (
        <ins className="adsbygoogle" style={{ display:"block", width:"100%", height:90 }}
             data-ad-client={adClient} data-ad-slot={adSlot} data-ad-format="rectangle"/>
      ) : (
        <>
          <div style={{ fontSize:10, color:"var(--text-faint)", fontFamily:"var(--font-mono)",
                        textTransform:"uppercase", letterSpacing:"0.1em" }}>Advertisement</div>
          <div style={{ fontSize:12, color:"var(--text-dim)", textAlign:"center", lineHeight:1.6 }}>
            <strong style={{ color:"var(--text)" }}>Remove ads + unlock Telegram delivery.</strong>
            <br/>Upgrade to Basic for ${29}/mo.
          </div>
          <a href="/signup?plan=basic"
             style={{ padding:"6px 18px", background:"var(--accent)", color:"#fff",
                      borderRadius:6, fontSize:11, fontWeight:600, textDecoration:"none",
                      fontFamily:"var(--font-mono)", letterSpacing:"0.05em" }}>
            Start 7-day trial →
          </a>
        </>
      )}
    </div>
  );
}

function Sparkline({ ticker, up }) {
  const w = 100, h = 36;
  const [realPts, setRealPts] = useState(null);

  useEffect(() => {
    if (!ticker) return;
    const ctrl = new AbortController();
    apiFetch(`/api/signals/${ticker}/spark`, { signal: ctrl.signal }).then(d => {
      if (d?.prices?.length > 1) setRealPts(d.prices);
    }).catch(() => {});
    return () => ctrl.abort();
  }, [ticker]);

  const pts = useMemo(() => {
    if (realPts) return realPts;
    let seed = (ticker || "X").split("").reduce((a,c) => a + c.charCodeAt(0), 0);
    const rand = () => { seed = (seed * 9301 + 49297) % 233280; return seed / 233280; };
    let v = 50;
    return Array.from({ length: 30 }, () => { v += (rand() - (up ? 0.4 : 0.6)) * 8; return v; });
  }, [ticker, up, realPts]);

  const lo = Math.min(...pts), hi = Math.max(...pts);
  const xs = i => pts.length <= 1 ? w / 2 : (i / (pts.length - 1)) * w;
  const ys = v => h - ((v - lo) / (hi - lo || 1)) * h;
  const realUp = realPts ? realPts[realPts.length - 1] >= realPts[0] : up;
  const color = realUp ? "var(--up)" : "var(--down)";
  return (
    <svg aria-hidden="true" className="sparkline" viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none">
      <path d={`M 0 ${h} ${pts.map((v,i) => `L ${xs(i)} ${ys(v)}`).join(" ")} L ${w} ${h} Z`} fill={color} opacity="0.15"/>
      <path d={`M ${xs(0)} ${ys(pts[0])} ${pts.map((v,i) => `L ${xs(i)} ${ys(v)}`).join(" ")}`} stroke={color} strokeWidth="1.2" fill="none"/>
    </svg>
  );
}

function PathSparkline({ path }) {
  if (!path || path.length < 2) return null;
  const w = 120, h = 24;
  const lo = Math.min(...path), hi = Math.max(...path);
  const range = Math.max(hi - lo, 0.001);
  const xs = i => (i / (path.length - 1)) * w;
  const ys = v => h - ((v - lo) / range) * h;
  const up = path[path.length - 1] >= path[0];
  const color = up ? "var(--up)" : "var(--down)";
  const d = `M ${xs(0)} ${ys(path[0])} ` + path.map((v, i) => `L ${xs(i)} ${ys(v)}`).join(" ");
  return (
    <svg aria-hidden="true" viewBox={`0 0 ${w} ${h}`} style={{ width: "100%", height: "100%", display: "block" }}>
      <path d={d} stroke={color} strokeWidth="1.5" fill="none" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx={xs(path.length - 1)} cy={ys(path[path.length - 1])} r="2" fill={color} />
      {hi > 0 && lo < 0 && (
        <line x1={0} y1={ys(0)} x2={w} y2={ys(0)} stroke="var(--text-faint)" strokeWidth="0.5" strokeDasharray="2 2" />
      )}
    </svg>
  );
}
