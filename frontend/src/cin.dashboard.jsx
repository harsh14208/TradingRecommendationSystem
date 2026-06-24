/* global React */
// SIGNAL.TRADE cinematic — Signal Dashboard (real signals + rationale + Telegram preview).
const { useState: dUseState, useEffect: dUseEffect, useRef: dUseRef, useMemo: dUseMemo } = React;

// Human, non-alarming label for why a signal isn't delivered. Most non-delivered
// rows are simply below the confidence bar; lead with that framing rather than a
// blunt "not sent". `short` returns a compact uppercase chip.
function deliveryLabel(status, short) {
  const s = (status || "").toLowerCase();
  if (s.includes("mean-reversion setup") || s.includes("oversold")) return short ? "NO MR SETUP" : "No mean-reversion setup";
  if (s.includes("floor") || s.includes("confidence")) return short ? "BELOW THRESHOLD" : "Below confidence threshold";
  if (s.includes("intraday") || s.includes("style")) return short ? "STYLE OFF" : "Intraday style — not delivered";
  if (s.includes("sector")) return short ? "SECTOR PAUSED" : "Sector temporarily paused";
  if (s.includes("regime") || s.includes("long-only")) return short ? "NOT BUY" : "Not a buy signal";
  if (s.includes("blocked") || s.includes("edge")) return short ? "PAUSED" : "Ticker paused — no mean-reversion edge";
  return short ? "BELOW THRESHOLD" : "Below delivery threshold";
}

function sigColor(signal) {
  return signal === "SELL" ? "var(--bear)" : signal === "HOLD" ? "var(--neutral)" : "var(--bull)";
}
function sigRaw(signal) {
  return signal === "SELL" ? "251,77,109" : signal === "HOLD" ? "251,191,36" : "34,211,238";
}

function seriesFor(s, n = 90) {
  const raw = genSeries((s.seed || 1) * 97 + 5, n, 100, s.drift || 0, s.volatility || 0.02);
  const k = s.px / raw[raw.length - 1];
  return raw.map((v) => v * k);
}
function sparkForSignal(s) { return seriesFor(s, 30).slice(-30); }

// Real mini-sparkline data (last ~30 daily closes) from /api/signals/{tk}/spark,
// cached per ticker. Falls back to the synthetic series only while loading or if
// the fetch fails — the card graph should reflect real price action.
const _sparkCache = {};
function useRealSpark(ticker) {
  const [prices, setPrices] = dUseState(() => _sparkCache[ticker] || null);
  dUseEffect(() => {
    if (!ticker || _sparkCache[ticker]) { if (_sparkCache[ticker]) setPrices(_sparkCache[ticker]); return; }
    let live = true;
    apiFetch(`/api/signals/${encodeURIComponent(ticker)}/spark`)
      .then((d) => {
        const p = d && Array.isArray(d.prices) ? d.prices : null;
        if (p && p.length > 1) { _sparkCache[ticker] = p; if (live) setPrices(p); }
      })
      .catch(() => {});
    return () => { live = false; };
  }, [ticker]);
  return prices;
}
function winSparkForSignal(s) {
  const rnd = mulberry32((s.seed || 1) * 31 + 7);
  const out = [];
  for (let i = 0; i < 12; i++) out.push((s.win || 60) + (rnd() - 0.5) * 14);
  out[11] = s.win || 60;
  return out;
}

function BigChart({ s }) {
  const data = seriesFor(s, 90);
  const w = 720, h = 280;
  const min = Math.min(...data), max = Math.max(...data);
  const rng = max - min || 1;
  const pts = data.map((v, i) => [(i / (data.length - 1)) * w, h - 16 - ((v - min) / rng) * (h - 40)]);
  const d = pts.map((p, i) => `${i ? "L" : "M"}${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(" ");
  const col = sigColor(s.signal), colRaw = sigRaw(s.signal);
  const mi = data.length - 12;
  const marker = pts[mi];
  const last = pts[pts.length - 1];
  const gridY = [0.25, 0.5, 0.75].map((f) => 16 + (h - 40) * f);
  // entry / stop / target horizontal guides (map price → y)
  const yFor = (price) => h - 16 - ((price - min) / rng) * (h - 40);
  const guides = s.entry ? [
    { p: s.target, c: "var(--bull)", t: "TP" },
    { p: s.entry, c: "var(--text-dim)", t: "ENTRY" },
    { p: s.stop, c: "var(--bear)", t: "STOP" },
  ].filter((g) => g.p >= min && g.p <= max) : [];
  return (
    <svg viewBox={`0 0 ${w} ${h}`} style={{ width: "100%", height: "auto", display: "block" }}>
      <defs>
        <linearGradient id="bigfill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={`rgb(${colRaw})`} stopOpacity="0.18"></stop>
          <stop offset="100%" stopColor={`rgb(${colRaw})`} stopOpacity="0"></stop>
        </linearGradient>
      </defs>
      {gridY.map((y, i) => (
        <g key={i}>
          <line x1="0" x2={w} y1={y} y2={y} stroke="rgba(255,255,255,0.045)" strokeDasharray="2 5"></line>
          <text x={w - 4} y={y - 5} textAnchor="end" fontSize="9.5" fill="var(--text-faint)" fontFamily="var(--font-mono)">${(max - rng * ((y - 16) / (h - 40))).toFixed(0)}</text>
        </g>
      ))}
      {guides.map((g, i) => (
        <g key={"g" + i}>
          <line x1="0" x2={w} y1={yFor(g.p)} y2={yFor(g.p)} stroke={g.c} strokeWidth="1" strokeDasharray="1 4" opacity="0.55"></line>
          <text x="4" y={yFor(g.p) - 4} fontSize="8.5" fill={g.c} fontFamily="var(--font-mono)" letterSpacing="0.08em">{g.t} {g.p}</text>
        </g>
      ))}
      <path d={`${d} L${w},${h} L0,${h} Z`} fill="url(#bigfill)"></path>
      <path d={d} fill="none" stroke={col} strokeWidth="1.8" strokeLinejoin="round"></path>
      <line x1={marker[0]} x2={marker[0]} y1={12} y2={h - 14} stroke={`rgba(${colRaw},0.3)`} strokeDasharray="3 4"></line>
      <circle cx={marker[0]} cy={marker[1]} r="4.5" fill={col} stroke="#0A0E17" strokeWidth="2"></circle>
      <g transform={`translate(${Math.min(marker[0] + 8, w - 130)}, ${Math.max(14, marker[1] - 34)})`}>
        <rect width="118" height="24" rx="5" fill="rgba(10,14,23,0.85)" stroke={`rgba(${colRaw},0.4)`}></rect>
        <text x="9" y="16" fontSize="10" fontWeight="700" fill={col} fontFamily="var(--font-mono)" letterSpacing="0.06em">{s.signal} · {s.conf}% CONF</text>
      </g>
      <circle cx={last[0]} cy={last[1]} r="3.4" fill={col}></circle>
    </svg>
  );
}

// Real OHLCV price chart for the dashboard — reuses the shared <Chart>
// (LightweightCharts, /api/chart, entry/stop/target guides) with a date-range
// selector. Replaces the synthetic BigChart so the dashboard shows real prices.
function DashChart({ s }) {
  const [period, setPeriod] = dUseState("1M");
  const sig = { ticker: s.tk, entry: s.entry, stop: s.stop, target: s.target, action: s.signal };
  return (
    <div>
      <div style={{ display: "flex", justifyContent: "flex-end", gap: 4, marginBottom: 8 }}>
        {["1D", "1W", "1M", "YTD", "ALL"].map((p) => (
          <button key={p} onClick={() => setPeriod(p)} className="mono"
            style={{ fontSize: 10, fontWeight: 700, padding: "3px 9px", borderRadius: 5, cursor: "pointer",
              border: "1px solid var(--line)",
              background: period === p ? "var(--accent)" : "transparent",
              color: period === p ? "#052418" : "var(--text-dim)" }}>{p}</button>
        ))}
      </div>
      <Chart signal={sig} style="area" period={period}></Chart>
    </div>
  );
}

function WatchRow({ s, active, onClick }) {
  const undeliverable = s.deliverable === false;
  const realSpark = useRealSpark(s.tk);
  const sparkData = realSpark && realSpark.length > 1 ? realSpark : sparkForSignal(s);
  return (
    <button onClick={onClick} style={{
      display: "grid", gridTemplateColumns: "1fr auto", gap: "2px 10px", alignItems: "center",
      width: "100%", textAlign: "left", padding: "11px 14px",
      background: active ? "var(--panel-2)"
        : undeliverable ? "repeating-linear-gradient(135deg, rgba(120,120,120,0.05) 0 8px, transparent 8px 16px)"
        : "transparent",
      border: "none",
      borderLeft: active ? `2px solid ${sigColor(s.signal)}`
        : undeliverable ? "2px solid rgba(120,120,120,0.4)" : "2px solid transparent",
      borderBottom: "1px solid var(--line-soft)", transition: "background 0.18s var(--ease)", cursor: "pointer",
      opacity: undeliverable && !active ? 0.7 : 1,
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <span className="mono" style={{ fontWeight: 700, fontSize: 13, color: "var(--text)" }}>{s.tk}</span>
        <SignalBadge signal={s.signal}></SignalBadge>
        <span className="mono" title={`Confidence ${Math.round(s.conf || 0)}%`}
          style={{ fontSize: 10, fontWeight: 700, letterSpacing: "0.03em",
            color: (s.conf || 0) >= 70 ? "var(--bull)" : (s.conf || 0) >= 50 ? "var(--neutral)" : "var(--text-dim)" }}>
          {Math.round(s.conf || 0)}%
        </span>
        {!!s.optionStrategy && (
          <span title="Options VRP" className="mono"
            style={{ fontSize: 8.5, fontWeight: 800, letterSpacing: "0.06em", color: "var(--warn)",
              border: "1px solid var(--warn)", borderRadius: 3, padding: "0 4px" }}>OPT</span>
        )}
        {s.deliverable === false && (
          <span title={s.deliveryStatus ? deliveryLabel(s.deliveryStatus) + " — " + s.deliveryStatus : deliveryLabel(s.deliveryStatus)}
            className="mono" style={{ fontSize: 9, fontWeight: 700, color: "var(--text-dim)",
              background: "rgba(120,120,120,0.14)", border: "1px solid rgba(120,120,120,0.30)",
              borderRadius: 3, padding: "0 4px", letterSpacing: "0.04em" }}>{deliveryLabel(s.deliveryStatus, true)}</span>
        )}
      </div>
      <Spark data={sparkData} w={62} h={22} color={(sparkData[sparkData.length - 1] - sparkData[0]) >= 0 ? "bull" : "bear"} fill={false} sw={1.2}></Spark>
      <span className="mono dim" style={{ fontSize: 11.5 }}>${s.px.toLocaleString("en-US", { minimumFractionDigits: 2 })}</span>
      <span className={`mono ${s.chgPct >= 0 ? "bull" : "bear"}`} style={{ fontSize: 11.5, textAlign: "right" }}>
        {s.chgPct >= 0 ? "+" : ""}{s.chgPct.toFixed(2)}%
      </span>
    </button>
  );
}

function PlanStat({ label, value, color }) {
  return (
    <div style={{ flex: 1, minWidth: 64 }}>
      <div className="kicker" style={{ marginBottom: 4 }}>{label}</div>
      <span className="mono" style={{ fontSize: 14, fontWeight: 600, color: color || "var(--text)" }}>{value}</span>
    </div>
  );
}

function SourceChip({ s }) {
  return <span className="mono" style={{ fontSize: 9.5, letterSpacing: "0.08em", color: "var(--text-dim)", border: "1px solid var(--line)", borderRadius: 4, padding: "2px 6px" }}>{s}</span>;
}

function RationaleItem({ r }) {
  const col = r.sentiment === "pos" ? "var(--bull)" : r.sentiment === "neg" ? "var(--bear)" : "var(--neutral)";
  return (
    <div style={{ display: "grid", gridTemplateColumns: "auto 1fr", gap: 10, padding: "11px 0", borderBottom: "1px solid var(--line-soft)" }}>
      <span className="mono" style={{ fontSize: 9, fontWeight: 700, letterSpacing: "0.06em", color: col, alignSelf: "start", marginTop: 2, border: `1px solid ${col}`, borderRadius: 4, padding: "2px 5px", height: "fit-content" }}>{r.src}</span>
      <div>
        <div style={{ fontSize: 12.5, fontWeight: 500, lineHeight: 1.4, color: "var(--text)" }}>{r.head}</div>
        <div style={{ fontSize: 11.5, color: "var(--text-dim)", lineHeight: 1.5, marginTop: 3, textWrap: "pretty" }}>{r.body}</div>
        <div className="kicker" style={{ marginTop: 4, color: "var(--text-ghost)" }}>{r.meta}</div>
      </div>
    </div>
  );
}

function Chevron({ open }) {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"
      style={{ color: "var(--text-faint)", transition: "transform 0.2s var(--ease)", transform: open ? "rotate(180deg)" : "none", flex: "none" }}>
      <path d="m6 9 6 6 6-6"></path>
    </svg>
  );
}

function ThresholdToggle({ count, open, onToggle }) {
  return (
    <button type="button" onClick={onToggle}
      style={{ width: "100%", display: "flex", alignItems: "center", gap: 10,
        padding: "8px 14px", background: "var(--panel-2)", border: "none",
        borderBottom: open ? "1px solid var(--line-soft)" : "none",
        textAlign: "left", cursor: "pointer" }}>
      <span className="kicker" style={{ color: "var(--text-faint)" }}>BELOW DELIVERY THRESHOLD</span>
      <span style={{ flex: 1, height: 1, background: "var(--line)" }}></span>
      <span className="kicker" style={{ color: "var(--text-ghost)" }}>{count}</span>
      <Chevron open={open}></Chevron>
    </button>
  );
}

// Panel that collapses on mobile (≤860px) via a tappable header; always open on
// desktop. Lets the dashboard keep the main chart panel visible while the
// secondary panels fold away on small screens.
function CollapsiblePanel({ label, labelColor, right, defaultOpen = true, hover = false, pad = 18, stretch = false, children }) {
  const mobile = useIsMobile();
  const [open, setOpen] = dUseState(defaultOpen);
  const isOpen = mobile ? open : true;
  return (
    <div className={`glass ${hover ? "glass-hover" : ""}`} style={{ overflow: "hidden", alignSelf: stretch ? "stretch" : "start", height: stretch ? "100%" : undefined }}>
      <button type="button" onClick={() => mobile && setOpen((o) => !o)}
        style={{ width: "100%", display: "flex", alignItems: "center", gap: 10, padding: `${pad}px ${pad}px ${isOpen ? 12 : pad}px`,
          background: "none", border: "none", textAlign: "left", cursor: mobile ? "pointer" : "default" }}>
        <span className="kicker" style={{ color: labelColor }}>{label}</span>
        <span style={{ marginLeft: "auto", display: "inline-flex", alignItems: "center", gap: 10 }}>
          {right}
          {mobile && <Chevron open={open}></Chevron>}
        </span>
      </button>
      {isOpen && <div style={{ padding: `0 ${pad}px ${pad}px` }}>{children}</div>}
    </div>
  );
}

/* Fallback sector mapping for tickers that don't carry sector_etf from the
   backend. Covers the most liquid names so the sector context card rarely blanks. */
const _TICKER_TO_SECTOR = {
  AAPL:"XLK", MSFT:"XLK", NVDA:"XLK", AVGO:"XLK", AMD:"XLK", INTC:"XLK", QCOM:"XLK", CRM:"XLK", ADBE:"XLK", ORCL:"XLK", IBM:"XLK", CSCO:"XLK", ACN:"XLK", PYPL:"XLK", SHOP:"XLK", NFLX:"XLK", AMAT:"XLK", LRCX:"XLK", KLAC:"XLK", MRVL:"XLK", PANW:"XLK", SNOW:"XLK", PLTR:"XLK", CRWD:"XLK", DDOG:"XLK", NET:"XLK", TEAM:"XLK", ZM:"XLK", UBER:"XLK", LYFT:"XLK", ABNB:"XLK", DKNG:"XLK", RBLX:"XLK", SNAP:"XLK", PINS:"XLK", TWLO:"XLK", SQ:"XLK", HOOD:"XLK", COIN:"XLK", MSTR:"XLK", SMCI:"XLK",
  JNJ:"XLV", PFE:"XLV", UNH:"XLV", LLY:"XLV", ABBV:"XLV", TMO:"XLV", ABT:"XLV", MRK:"XLV", DHR:"XLV", AMGN:"XLV", GILD:"XLV", BMY:"XLV", CI:"XLV", ELV:"XLV", CVS:"XLV", HUM:"XLV", REGN:"XLV", VRTX:"XLV", BIIB:"XLV", ZTS:"XLV", ISRG:"XLV", BSX:"XLV", SYK:"XLV", EW:"XLV", MDT:"XLV", BDX:"XLV", A:"XLV", DXCM:"XLV",
  JPM:"XLF", BAC:"XLF", WFC:"XLF", GS:"XLF", MS:"XLF", C:"XLF", BLK:"XLF", AXP:"XLF", SPGI:"XLF", PNC:"XLF", USB:"XLF", TFC:"XLF", COF:"XLF", SCHW:"XLF", BK:"XLF", STT:"XLF", CME:"XLF", ICE:"XLF", MCO:"XLF", AON:"XLF", CB:"XLF", MMC:"XLF", PGR:"XLF", TRV:"XLF", ALL:"XLF", MET:"XLF", AIG:"XLF", WTW:"XLF", RJF:"XLF", RF:"XLF", KEY:"XLF", HBAN:"XLF", FITB:"XLF", CFG:"XLF", JEF:"XLF", NLY:"XLF",
  AMZN:"XLY", TSLA:"XLY", HD:"XLY", MCD:"XLY", NKE:"XLY", SBUX:"XLY", LOW:"XLY", BKNG:"XLY", TJX:"XLY", F:"XLY", GM:"XLY", MAR:"XLY", RCL:"XLY", CCL:"XLY", LULU:"XLY", ETSY:"XLY", ORLY:"XLY", AZO:"XLY", AAP:"XLY", DG:"XLY", DLTR:"XLY", KMX:"XLY", BBY:"XLY", YUM:"XLY", DPZ:"XLY", CMG:"XLY", DRI:"XLY", NCLH:"XLY", CZR:"XLY", WYNN:"XLY", MGM:"XLY", LVS:"XLY", PENN:"XLY",
  GOOGL:"XLC", GOOG:"XLC", META:"XLC", VZ:"XLC", T:"XLC", CMCSA:"XLC", DIS:"XLC", TMUS:"XLC", CHTR:"XLC", FOXA:"XLC", WBD:"XLC", PARA:"XLC", EA:"XLC", ATVI:"XLC", TTWO:"XLC", MTCH:"XLC", IAC:"XLC", LYV:"XLC", SPOT:"XLC",
  GE:"XLI", HON:"XLI", UNP:"XLI", BA:"XLI", CAT:"XLI", RTX:"XLI", LMT:"XLI", UPS:"XLI", ABB:"XLI", DE:"XLI", ETN:"XLI", ITW:"XLI", GD:"XLI", NOC:"XLI", CSX:"XLI", NSC:"XLI", WM:"XLI", RSG:"XLI", URI:"XLI", CMI:"XLI", PH:"XLI", PCAR:"XLI", OTIS:"XLI", CAR:"XLI",
  WMT:"XLP", PG:"XLP", KO:"XLP", PEP:"XLP", COST:"XLP", MO:"XLP", EL:"XLP", GIS:"XLP", KMB:"XLP", CL:"XLP", KHC:"XLP", STZ:"XLP", MDLZ:"XLP", MNST:"XLP", KR:"XLP", SYY:"XLP", ADM:"XLP", KDP:"XLP", CHD:"XLP", CLX:"XLP", HSY:"XLP", MKC:"XLP", CAG:"XLP", CPB:"XLP", TSN:"XLP", HRL:"XLP", BFb:"XLP", TAP:"XLP",
  XOM:"XLE", CVX:"XLE", COP:"XLE", EOG:"XLE", SLB:"XLE", OXY:"XLE", MPC:"XLE", VLO:"XLE", PSX:"XLE", WMB:"XLE", KMI:"XLE", OKE:"XLE", TRGP:"XLE", LNG:"XLE", MRO:"XLE", DVN:"XLE", FANG:"XLE", PXD:"XLE", HAL:"XLE", BKR:"XLE", AM:"XLE", CEQP:"XLE", ET:"XLE", EPd:"XLE",
  NEE:"XLU", SO:"XLU", DUK:"XLU", D:"XLU", AEP:"XLU", SRE:"XLU", EXC:"XLU", XEL:"XLU", ED:"XLU", PPL:"XLU", ES:"XLU", WEC:"XLU", DTE:"XLU", AEE:"XLU", FE:"XLU", EIX:"XLU", PCG:"XLU", CNP:"XLU", NI:"XLU", NRG:"XLU",
  PLD:"XLRE", AMT:"XLRE", EQIX:"XLRE", CCI:"XLRE", PSA:"XLRE", O:"XLRE", SPG:"XLRE", VICI:"XLRE", WELL:"XLRE", DLR:"XLRE", AVB:"XLRE", EQR:"XLRE", UDR:"XLRE", MAA:"XLRE", CPT:"XLRE", BXP:"XLRE", VTR:"XLRE", HST:"XLRE", ESS:"XLRE", ARE:"XLRE",
  LIN:"XLB", SHW:"XLB", FCX:"XLB", NEM:"XLB", ECL:"XLB", APD:"XLB", DOW:"XLB", DD:"XLB", NUE:"XLB", VMC:"XLB", MLM:"XLB", CTVA:"XLB", FMC:"XLB", MOS:"XLB", CF:"XLB", PXD:"XLB", OKE:"XLB", STLD:"XLB", RS:"XLB", CMC:"XLB", NEM:"XLB", GOLD:"XLB", FNV:"XLB", WPM:"XLB",
  SPY:"SPY", QQQ:"QQQ", DIA:"DIA", IWM:"IWM", VOO:"VOO", IVV:"IVV", VTI:"VTI", VEA:"VEA", VWO:"VWO", IEFA:"IEFA", EFA:"EFA",
};

const _sectorCache = { data: null, ts: 0, loading: false, promise: null };
function _fetchSectors() {
  const now = Date.now();
  if (_sectorCache.data && now - _sectorCache.ts < 600000) return Promise.resolve(_sectorCache.data);
  if (_sectorCache.promise) return _sectorCache.promise;
  _sectorCache.loading = true;
  _sectorCache.promise = apiFetch("/api/market/sectors")
    .then((d) => { _sectorCache.data = Array.isArray(d) ? d : []; _sectorCache.ts = Date.now(); return _sectorCache.data; })
    .catch(() => { _sectorCache.data = _sectorCache.data || []; return _sectorCache.data; })
    .finally(() => { _sectorCache.loading = false; _sectorCache.promise = null; });
  return _sectorCache.promise;
}

function SectorContextPanel({ s }) {
  const [sectors, setSectors] = dUseState(_sectorCache.data || []);
  dUseEffect(() => { let mounted = true; _fetchSectors().then((d) => { if (mounted) setSectors(d); }); return () => { mounted = false; }; }, []);

  const etf = s.sectorEtf || _TICKER_TO_SECTOR[s.tk?.toUpperCase()] || null;
  const idx = etf ? sectors.findIndex((x) => x.etf === etf) : -1;
  const sec = idx >= 0 ? sectors[idx] : null;
  const fmt = (v) => v == null ? "—" : `${v >= 0 ? "+" : ""}${v.toFixed(2)}%`;
  const color = (v) => v == null ? "var(--text-faint)" : v >= 0 ? "var(--bull)" : "var(--bear)";

  return (
    <CollapsiblePanel label="SECTOR CONTEXT" hover defaultOpen={false} stretch>
      {!sec ? (
        <div style={{ fontSize: 12.5, color: "var(--text-faint)", lineHeight: 1.55 }}>
          {etf ? `Loading ${etf} context…` : "No sector data for this ticker."}
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          <div style={{ display: "flex", alignItems: "flex-end", gap: 16 }}>
            <span className="mono" style={{ fontSize: 26, fontWeight: 700, color: color(sec.ret_1m) }}>{fmt(sec.ret_1m)}</span>
            <div style={{ marginBottom: 4 }}>
              <div style={{ fontSize: 13, fontWeight: 600 }}>{sec.name}</div>
              <div className="mono" style={{ fontSize: 11, color: "var(--text-dim)" }}>{sec.etf} · #{idx + 1} of {sectors.length}</div>
            </div>
          </div>

          <div style={{ display: "flex", gap: 10, flexWrap: "wrap", fontSize: 11 }}>
            <span className="mono"><span style={{ color: "var(--text-faint)" }}>1D</span> <span style={{ color: color(sec.ret_1d) }}>{fmt(sec.ret_1d)}</span></span>
            <span className="mono"><span style={{ color: "var(--text-faint)" }}>1W</span> <span style={{ color: color(sec.ret_1w) }}>{fmt(sec.ret_1w)}</span></span>
            <span className="mono"><span style={{ color: "var(--text-faint)" }}>3M</span> <span style={{ color: color(sec.ret_3m) }}>{fmt(sec.ret_3m)}</span></span>
            <span className="mono"><span style={{ color: "var(--text-faint)" }}>YTD</span> <span style={{ color: color(sec.ret_ytd) }}>{fmt(sec.ret_ytd)}</span></span>
          </div>
        </div>
      )}
    </CollapsiblePanel>
  );
}

function OptionsVRPPanel({ s }) {
  const hasOptions = !!s.optionStrategy;
  if (!hasOptions) return null;

  const fmtPct = (v) => v == null ? "—" : `${v >= 0 ? "+" : ""}${v.toFixed(2)}%`;
  const fmtMove = (v) => v == null ? "—" : `${(v * 100).toFixed(2)}%`;
  const legs = Array.isArray(s.optionLegs) ? s.optionLegs : [];

  return (
    <CollapsiblePanel label="OPTIONS VRP" labelColor="var(--warn)" right={<span className="kicker">{s.optionStrategy.replace(/_/g, " ").toUpperCase()}</span>} defaultOpen={false} pad={18}>
      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        <div style={{ fontSize: 12.5, color: "var(--text-dim)", lineHeight: 1.55 }}>
          This is an options-derived signal: the underlying {s.optionUnderlyingAction || s.signal} thesis is combined with an options volatility view.
          Rich options = the market is pricing a larger move than the engine forecasts.
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(120px, 1fr))", gap: 10 }}>
          <div><div className="kicker" style={{ marginBottom: 3 }}>IMPLIED MOVE</div><span className="mono" style={{ fontSize: 13 }}>{fmtMove(s.optionImplMove)}</span></div>
          <div><div className="kicker" style={{ marginBottom: 3 }}>FORECAST MOVE</div><span className="mono" style={{ fontSize: 13 }}>{fmtMove(s.optionForecastMove)}</span></div>
          <div><div className="kicker" style={{ marginBottom: 3 }}>RICHNESS</div><span className="mono" style={{ fontSize: 13, color: s.optionRichness > 1 ? "var(--bull)" : "var(--neutral)" }}>{s.optionRichness?.toFixed(2) ?? "—"}</span></div>
          <div><div className="kicker" style={{ marginBottom: 3 }}>EXP GAIN</div><span className="mono" style={{ fontSize: 13, color: "var(--bull)" }}>{fmtPct(s.optionExpGain)}</span></div>
          <div><div className="kicker" style={{ marginBottom: 3 }}>MAX LOSS</div><span className="mono" style={{ fontSize: 13, color: "var(--bear)" }}>{fmtPct(s.optionMaxLoss)}</span></div>
          <div><div className="kicker" style={{ marginBottom: 3 }}>EARNINGS</div><span className="mono" style={{ fontSize: 13 }}>{s.optionDaysToEarnings != null ? `${s.optionDaysToEarnings}d` : "—"}</span></div>
        </div>

        {legs.length > 0 && (
          <div>
            <div className="kicker" style={{ marginBottom: 8 }}>LEGS</div>
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {legs.map((leg, i) => (
                <div key={i} style={{ display: "flex", alignItems: "center", gap: 10, padding: "8px 10px", background: "var(--bg-2)", borderRadius: 6, border: "1px solid var(--line-soft)" }}>
                  <SignalBadge signal={leg.side === "sell" || leg.position === "short" ? "SELL" : "BUY"} size="sm"></SignalBadge>
                  <span className="mono" style={{ fontSize: 12 }}>{leg.option_type?.toUpperCase()} {leg.strike != null ? `$${leg.strike}` : ""} {leg.expiry ? `· ${leg.expiry}` : ""}</span>
                  <span className="mono" style={{ fontSize: 11, color: "var(--text-faint)", marginLeft: "auto" }}>{leg.quantity != null ? `${leg.quantity}×` : ""}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        <div style={{ fontSize: 10.5, color: "var(--text-ghost)", lineHeight: 1.5 }}>
          Options VRP signals are informational only. Reward/risk can be attractive but tail risk is real — size accordingly.
        </div>
      </div>
    </CollapsiblePanel>
  );
}

function TelegramPreview({ log }) {
  return (
    <div className="glass" style={{ padding: 16, alignSelf: "start" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
        <span className="kicker">TELEGRAM DELIVERY</span>
        <span className="kicker" style={{ marginLeft: "auto", color: "var(--bull)", display: "inline-flex", gap: 6, alignItems: "center" }}><LiveDot></LiveDot> @signaltradebot</span>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {(log || TELEGRAM_FEED || []).map((m, i) => {
          const out = m.dir === "out";
          const col = m.verb === "SELL" ? "var(--bear)" : m.verb === "BUY" ? "var(--bull)" : "var(--neutral)";
          return (
            <div key={i} style={{ alignSelf: out ? "flex-start" : "flex-end", maxWidth: "92%" }}>
              <div style={{
                background: out ? "rgba(255,255,255,0.04)" : "var(--bull-soft)",
                border: `1px solid ${out ? "var(--line)" : "rgba(34,211,238,0.2)"}`,
                borderRadius: out ? "4px 10px 10px 10px" : "10px 10px 4px 10px",
                padding: "9px 12px",
              }}>
                {out ? (
                  <React.Fragment>
                    <div style={{ display: "flex", alignItems: "center", gap: 7, marginBottom: 5 }}>
                      <span className="mono" style={{ fontSize: 10, fontWeight: 700, color: col, letterSpacing: "0.06em" }}>{m.verb}</span>
                      <span className="mono" style={{ fontSize: 11.5, fontWeight: 700 }}>{m.tk}</span>
                      <span className="mono dim" style={{ fontSize: 11 }}>${m.px}</span>
                    </div>
                    <div className="mono" style={{ fontSize: 10.5, color: "var(--text-dim)", lineHeight: 1.55, whiteSpace: "pre-line" }}>{m.body}</div>
                  </React.Fragment>
                ) : (
                  <div style={{ fontSize: 12, color: "var(--text)" }}>{m.body}</div>
                )}
              </div>
              <div className="kicker" style={{ marginTop: 3, textAlign: out ? "left" : "right", color: "var(--text-ghost)" }}>{m.time} ET</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function PageDashboard({ signals: propSignals, tickerTape, log: propLog, loading, onSend, onSkip, onReview, onNote, onPriceAlert }) {
  const signalList = propSignals && propSignals.length ? propSignals : (typeof SIGNALS !== "undefined" ? SIGNALS : []);
  const [tk, setTk] = dUseState(() => signalList[0]?.tk || "NVDA");
  const [query, setQuery] = dUseState("");
  const [actionFilter, setActionFilter] = dUseState("ALL");
  const [styleFilter, setStyleFilter] = dUseState("ALL");
  const [minConf, setMinConf] = dUseState(0);
  const [note, setNote] = dUseState("");
  const [optionsOpen, setOptionsOpen] = dUseState(true);
  const [liveBdtOpen, setLiveBdtOpen] = dUseState(false);
  const [optionsBdtOpen, setOptionsBdtOpen] = dUseState(false);

  const q = query.trim().toLowerCase();
  const filtered = dUseMemo(() => signalList.filter((s) => {
    if (q && !s.tk.toLowerCase().includes(q) && !(s.name || "").toLowerCase().includes(q)) return false;
    if (actionFilter !== "ALL" && s.signal !== actionFilter) return false;
    if (styleFilter !== "ALL" && s.style !== styleFilter) return false;
    if (s.conf < minConf) return false;
    return true;
  }), [signalList, q, actionFilter, styleFilter, minConf]);

  const liveSignals = filtered.filter((s) => !s.optionStrategy);
  const optionsSignals = filtered.filter((s) => !!s.optionStrategy);
  const liveDeliverable = liveSignals.filter((s) => s.deliverable !== false);
  const liveThreshold = liveSignals.filter((s) => s.deliverable === false);
  const optionsDeliverable = optionsSignals.filter((s) => s.deliverable !== false);
  const optionsThreshold = optionsSignals.filter((s) => s.deliverable === false);

  dUseEffect(() => { if (filtered.length && !filtered.find((x) => x.tk === tk)) setTk(filtered[0].tk); }, [filtered]);
  dUseEffect(() => { const found = signalList.find((x) => x.tk === tk); if (found) setNote(found.notes || ""); }, [tk, signalList]);

  const s = filtered.find((x) => x.tk === tk) || filtered[0];
  const winSpark = s ? winSparkForSignal(s) : [];
  const clearFilters = () => { setQuery(""); setActionFilter("ALL"); setStyleFilter("ALL"); setMinConf(0); };
  if (!s) {
    return (
      <div className="page wrap" style={{ paddingTop: 24, paddingBottom: 56 }}>
        <div className="glass" style={{ padding: 40, textAlign: "center", maxWidth: 480, margin: "0 auto" }}>
          <div className="kicker" style={{ color: "var(--text-faint)", marginBottom: 16 }}>NO SIGNALS MATCH FILTERS</div>
          <button className="btn" onClick={clearFilters}>Clear filters</button>
        </div>
      </div>
    );
  }
  return (
    <div className="page wrap" style={{ paddingTop: 24, paddingBottom: 56 }}>
      <div className="dash-grid">
        {/* Signal feed */}
        <aside className="glass" style={{ padding: 0, overflow: "hidden", alignSelf: "start" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "13px 14px", borderBottom: "1px solid var(--line)" }}>
            <span className="kicker">SIGNAL FEED</span>
            <span className="kicker" style={{ marginLeft: "auto", color: "var(--bull)", display: "inline-flex", gap: 6, alignItems: "center" }}><LiveDot></LiveDot> {liveSignals.length} LIVE</span>
          </div>
          <div style={{ padding: "10px 12px", display: "flex", flexDirection: "column", gap: 8, borderBottom: "1px solid var(--line-soft)" }}>
            <input type="text" placeholder="Search ticker or name…" value={query} onChange={(e) => setQuery(e.target.value)}
              style={{ width: "100%", background: "var(--bg-2)", border: "1px solid var(--line)", borderRadius: 6, padding: "7px 10px", color: "var(--text)", fontSize: 12 }} />
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              {[["ALL","All"],["BUY","Buy"],["SELL","Sell"],["HOLD","Hold"]].map(([k,l]) => (
                <button key={k} className={`btn xs ${actionFilter === k ? "primary" : "ghost"}`} onClick={() => setActionFilter(k)} style={{ fontSize: 11, padding: "4px 8px" }}>{l}</button>
              ))}
              <select value={styleFilter} onChange={(e) => setStyleFilter(e.target.value)}
                style={{ background: "var(--bg-2)", border: "1px solid var(--line)", borderRadius: 6, color: "var(--text)", fontSize: 11, padding: "4px 8px" }}>
                <option value="ALL">All styles</option><option value="intraday">Intraday</option><option value="swing">Swing</option><option value="position">Position</option><option value="options_vrp">Options VRP</option>
              </select>
              <select value={minConf} onChange={(e) => setMinConf(Number(e.target.value))}
                style={{ background: "var(--bg-2)", border: "1px solid var(--line)", borderRadius: 6, color: "var(--text)", fontSize: 11, padding: "4px 8px" }}>
                <option value={0}>Any conf</option><option value={60}>≥60%</option><option value={70}>≥70%</option><option value={80}>≥80%</option>
              </select>
            </div>
          </div>
          <Defer ms={500} skeleton={<div style={{ padding: 14, display: "flex", flexDirection: "column", gap: 10 }}>{[0, 1, 2, 3, 4, 5].map((i) => <SkelBlock key={i} h={40}></SkelBlock>)}</div>}>
            <div>
              {liveDeliverable.map((x) => (
                <WatchRow key={x.tk} s={x} active={x.tk === tk} onClick={() => setTk(x.tk)}></WatchRow>
              ))}
              {liveThreshold.length > 0 && (
                <div style={{ borderTop: "1px solid var(--line)" }}>
                  <ThresholdToggle count={liveThreshold.length} open={liveBdtOpen} onToggle={() => setLiveBdtOpen((o) => !o)}></ThresholdToggle>
                  {liveBdtOpen && liveThreshold.map((x) => (
                    <WatchRow key={x.tk} s={x} active={x.tk === tk} onClick={() => setTk(x.tk)}></WatchRow>
                  ))}
                </div>
              )}

              {optionsSignals.length > 0 && (
                <div style={{ borderTop: "1px solid var(--line)" }}>
                  <button type="button" onClick={() => setOptionsOpen((o) => !o)}
                    style={{ width: "100%", display: "flex", alignItems: "center", gap: 10,
                      padding: "10px 14px", background: "var(--panel-2)", border: "none",
                      borderBottom: optionsOpen ? "1px solid var(--line-soft)" : "none",
                      textAlign: "left", cursor: "pointer" }}>
                    <span className="kicker" style={{ color: "var(--warn)" }}>OPTIONS VRP</span>
                    <span className="kicker" style={{ marginLeft: "auto", color: "var(--text-faint)" }}>{optionsSignals.length}</span>
                    <Chevron open={optionsOpen}></Chevron>
                  </button>
                  {optionsOpen && (
                    <React.Fragment>
                      {optionsDeliverable.map((x) => (
                        <WatchRow key={x.tk} s={x} active={x.tk === tk} onClick={() => setTk(x.tk)}></WatchRow>
                      ))}
                      {optionsThreshold.length > 0 && (
                        <div style={{ borderTop: "1px solid var(--line-soft)" }}>
                          <ThresholdToggle count={optionsThreshold.length} open={optionsBdtOpen} onToggle={() => setOptionsBdtOpen((o) => !o)}></ThresholdToggle>
                          {optionsBdtOpen && optionsThreshold.map((x) => (
                            <WatchRow key={x.tk} s={x} active={x.tk === tk} onClick={() => setTk(x.tk)}></WatchRow>
                          ))}
                        </div>
                      )}
                    </React.Fragment>
                  )}
                </div>
              )}
            </div>
          </Defer>
        </aside>

        {/* Main */}
        <main style={{ display: "flex", flexDirection: "column", gap: 14, minWidth: 0 }}>
          <div className="glass" style={{ padding: "18px 20px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 14, flexWrap: "wrap", marginBottom: 8 }}>
              <span className="mono" style={{ fontSize: 22, fontWeight: 700, letterSpacing: "-0.01em" }}>{s.tk}</span>
              <span className="dim" style={{ fontSize: 13 }}>{s.name}</span>
              <SignalBadge signal={s.signal} size="lg"></SignalBadge>
              <span className="kicker" style={{ border: "1px solid var(--line)", borderRadius: 4, padding: "2px 7px" }}>{s.style.toUpperCase()}</span>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginLeft: "auto" }}>
                <span className="kicker">CONFIDENCE</span>
                <ConfMeter conf={s.conf}></ConfMeter>
                <span className="mono" style={{ fontSize: 13, fontWeight: 700, color: s.conf >= 70 ? "var(--bull)" : "var(--neutral)" }}>{s.conf}%</span>
              </div>
            </div>
            <div style={{ display: "flex", alignItems: "baseline", gap: 12, marginBottom: 12, flexWrap: "wrap" }}>
              <span style={{ fontSize: 30, fontWeight: 700 }}><Num value={s.px} dp={2} prefix="$"></Num></span>
              <span className={`mono ${s.chgPct >= 0 ? "bull" : "bear"}`} style={{ fontSize: 14, fontWeight: 600 }}>{s.chgPct >= 0 ? "+" : ""}{s.chgPct.toFixed(2)}% today</span>
              <div style={{ display: "flex", gap: 6, marginLeft: "auto" }}>{s.sources.map((src) => <SourceChip key={src} s={src}></SourceChip>)}</div>
            </div>
            {s.deliverable === false && (
              <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, lineHeight: 1.4,
                color: "var(--text-dim)", background: "rgba(120,120,120,0.10)",
                border: "1px solid rgba(120,120,120,0.25)", borderRadius: 6,
                padding: "7px 11px", marginBottom: 12 }}>
                <span style={{ fontWeight: 700 }}>{deliveryLabel(s.deliveryStatus)}</span>
                <span className="dim">
                  {s.deliveryStatus || "below the delivery threshold"} — shown for context; no Telegram / EOD alert is sent.
                </span>
              </div>
            )}
            {/* Signal actions */}
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 14 }}>
              <button className="btn sm" onClick={() => onSend(s.id)} title="Shift+S">📡 Send</button>
              <button className="btn sm" onClick={() => onSkip(s.id)}>⏭ Skip</button>
              <button className="btn sm" onClick={() => onReview(s.id)}>✓ Reviewed</button>
              <button className="btn sm" onClick={() => onPriceAlert(s)}>🚨 Alert</button>
            </div>
            <Defer ms={700} skeleton={<SkelBlock h={260}></SkelBlock>}><DashChart s={s}></DashChart></Defer>
            {/* Trade plan */}
            <div style={{ display: "flex", gap: 16, flexWrap: "wrap", marginTop: 14, paddingTop: 14, borderTop: "1px solid var(--line-soft)" }}>
              {s.entry ? (
                <React.Fragment>
                  <PlanStat label="R : R" value={s.rr.toFixed(1)} color="var(--bull)"></PlanStat>
                  <PlanStat label="ENTRY" value={`$${s.entry}`}></PlanStat>
                  <PlanStat label="STOP" value={`$${s.stop}`} color="var(--bear)"></PlanStat>
                  <PlanStat label="TARGET" value={`$${s.target}`} color="var(--bull)"></PlanStat>
                  <PlanStat label="MKT CAP" value={s.mcap}></PlanStat>
                  <PlanStat label="P/E" value={s.pe}></PlanStat>
                </React.Fragment>
              ) : (
                <React.Fragment>
                  <PlanStat label="STATUS" value="No trade" color="var(--neutral)"></PlanStat>
                  <PlanStat label="MKT CAP" value={s.mcap}></PlanStat>
                  <PlanStat label="VOLUME" value={s.vol}></PlanStat>
                  <PlanStat label="P/E" value={s.pe}></PlanStat>
                </React.Fragment>
              )}
            </div>
          </div>

          <div className="dash-sub">
            <CollapsiblePanel label={`WIN RATE · ${s.tk} HISTORY`} hover defaultOpen={false} stretch>
              <div style={{ display: "flex", alignItems: "flex-end", gap: 16 }}>
                <span className="mono" style={{ fontSize: 26, fontWeight: 700, color: s.win >= 65 ? "var(--bull)" : "var(--neutral)" }}><Num value={s.win} dp={0}></Num>%</span>
                <Spark data={winSpark} w={130} h={40} color={s.win >= 65 ? "bull" : "neutral"}></Spark>
              </div>
              <div style={{ fontSize: 11.5, color: "var(--text-faint)", marginTop: 8 }}>14-day horizon · Bayesian-smoothed</div>
            </CollapsiblePanel>
            <SectorContextPanel s={s}></SectorContextPanel>
          </div>

          {/* Options VRP — shown only when the options engine fired */}
          <OptionsVRPPanel s={s}></OptionsVRPPanel>

          {/* AI Insight — under the center panel */}
          <CollapsiblePanel label="AI INSIGHT" labelColor="var(--bull)" right={<span className="kicker">WHY THIS FIRED</span>} defaultOpen={false} pad={20}>
            <Defer ms={850} skeleton={<div style={{ display: "flex", flexDirection: "column", gap: 10 }}><SkelBlock h={20}></SkelBlock><SkelBlock h={70}></SkelBlock><SkelBlock h={140}></SkelBlock></div>}>
              <div>
                <div style={{ fontSize: 14.5, fontWeight: 600, lineHeight: 1.45, marginBottom: 10, textWrap: "balance" }}>{s.headline}</div>
                <p style={{ fontSize: 12.5, color: "var(--text-dim)", lineHeight: 1.6, margin: "0 0 16px", textWrap: "pretty" }}>{s.narrative}</p>
                <div className="kicker" style={{ marginBottom: 4 }}>EVIDENCE · {s.sources.length} SOURCES AGREED</div>
                {s.rationale.map((r, i) => <RationaleItem key={tk + i} r={r}></RationaleItem>)}
                <div style={{ marginTop: 16, padding: "12px 14px", borderRadius: 8, background: "var(--bull-soft)", border: "1px solid rgba(34,211,238,0.18)" }}>
                  <div style={{ fontSize: 12, lineHeight: 1.55, color: "var(--text)" }}>
                    {s.tk} signals have closed <span className="bull" style={{ fontWeight: 700 }}>{s.win}% green</span> on the 14-day horizon historically, with risk-reward of {s.rr.toFixed(1)} on this setup.
                  </div>
                </div>
                {/* Journal note */}
                <div style={{ marginTop: 14 }}>
                  <div className="kicker" style={{ marginBottom: 6 }}>JOURNAL NOTE</div>
                  <textarea value={note} onChange={(e) => setNote(e.target.value)} placeholder="Why are you taking this signal?"
                    style={{ width: "100%", minHeight: 56, background: "var(--bg-2)", border: "1px solid var(--line)", borderRadius: 6, padding: "8px 10px", color: "var(--text)", fontSize: 12, resize: "vertical" }} />
                  <button className="btn sm" style={{ marginTop: 6 }} onClick={() => onNote(s.id, note)}>Save note</button>
                </div>
                <div style={{ fontSize: 10.5, color: "var(--text-ghost)", marginTop: 12, lineHeight: 1.5 }}>Educational only — not financial advice. Past performance does not predict future results.</div>
              </div>
            </Defer>
          </CollapsiblePanel>
        </main>

        {/* Delivery log — right rail */}
        <aside style={{ alignSelf: "start" }}>
          <DeliveryLog log={propLog}></DeliveryLog>
        </aside>
      </div>
    </div>
  );
}

Object.assign(window, { PageDashboard });
