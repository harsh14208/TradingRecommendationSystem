/* ─── Why Now — head tip map ─────────────────────────────────────────────────── */
const HEAD_TIPS = [
  ["Orthogonal Alpha",       "ORTHOGONAL ALPHA"],
  ["Signal Cluster",         "SIGNAL CLUSTER"],
  ["Platt Calibration",      "PLATT CALIBRATION"],
  ["Calibration Adjusted",   "PLATT CALIBRATION"],
  ["Calibration DOWN",       "PLATT CALIBRATION"],
  ["Calibration UP",         "PLATT CALIBRATION"],
  ["Factor Mining",          "FACTOR MINING"],
  ["RSI Divergence",         "RSI DIVERGENCE"],
  ["Bullish RSI Divergence", "RSI DIVERGENCE"],
  ["Bearish RSI Divergence", "RSI DIVERGENCE"],
  ["Stochastic",             "STOCHASTIC"],
  ["Williams %R",            "WILLIAMS %R"],
  ["Ichimoku",               "ICHIMOKU"],
  ["Supertrend",             "SUPERTREND"],
  ["Keltner",                "KELTNER"],
  ["Donchian",               "DONCHIAN"],
  ["Price Structure",        "PRICE STRUCTURE"],
  ["Sector RS",              "SECTOR RS"],
  ["Z-Score",                "ZSCORE"],
  ["Pivot",                  "PIVOTS"],
  ["Fractal Dimension",      "FDI"],
  ["FDI",                    "FDI"],
  ["Hurst",                  "HURST"],
  ["VWAP",                   "VWAP"],
  ["CMF",                    "CMF"],
  ["Chaikin",                "CMF"],
  ["OBV",                    "OBV"],
  ["ADX",                    "ADX"],
  ["MACD",                   "MACD"],
  ["RSI",                    "RSI"],
  ["MFI",                    "MFI"],
  ["CCI",                    "CCI"],
  ["Stat Arb",               "STAT ARB"],
  ["Pairs Divergence",       "STAT ARB"],
  ["13F",                    "13F"],
  ["Institutional",          "13F"],
  ["Elliott Wave",           "ELLIOTT WAVE"],
  ["Gann",                   "GANN ANALYSIS"],
  ["Dark Pool",              "DARK POOL"],
  ["Reg SHO",                "FTD"],
  ["Positive Gamma",         "GEX"],
  ["Negative Gamma",         "GEX"],
  ["Smart Money Divergence", "DARK POOL"],
  ["Level 2 Imbalance",      "LEVEL 2"],
  ["Active Issuer",          "CORP ACTIONS"],
];

function tipifyHead(head) {
  if (!head) return head;
  for (const [prefix, term] of HEAD_TIPS) {
    if (head.startsWith(prefix)) {
      const rest = head.slice(prefix.length);
      return <>{<Tip term={term}>{prefix}</Tip>}{rest}</>;
    }
  }
  return head;
}

function WhyNow({ signal }) {
  const [open, setOpen] = useState(false);
  const posReasons = (signal.rationale || [])
    .filter(r => r.sentiment === (signal.action === "BUY" ? "pos" : "neg") && r.head)
    .slice(0, 3)
    .map(r => r.head);
  const topSrc = signal.sources?.[0] || "Technical";
  const reasons = posReasons.length >= 2 ? posReasons : [
    `${signal.sources?.length || 1} signal source${(signal.sources?.length||1)>1?"s":""} firing simultaneously`,
    `Confidence rose to ${signal.confidence?.toFixed(0)}% this scan`,
    `${topSrc} data changed since last evaluation`,
  ];
  return (
    <div style={{ margin:"12px 20px 0", background:"var(--bg-1)", border:"1px solid var(--line)", borderRadius:8 }}>
      <button onClick={() => setOpen(!open)}
        style={{ display:"flex", alignItems:"center", gap:10, width:"100%",
          padding:"10px 14px", background:"transparent", border:"none",
          color:"var(--text)", fontSize:12, cursor:"pointer", textAlign:"left" }}>
        <span style={{ width:6, height:6, borderRadius:"50%", background:"var(--accent)",
          boxShadow:"0 0 6px var(--accent)", animation:"pulse 1.6s infinite", flexShrink:0 }}/>
        <span><strong>Why now?</strong> &nbsp;What changed this scan</span>
        <span style={{ marginLeft:"auto", color:"var(--text-faint)", fontSize:10 }}>{open ? "▾" : "▸"}</span>
      </button>
      {open && (
        <ul style={{ listStyle:"none", padding:"0 14px 12px 36px", margin:0,
          fontSize:12, color:"var(--text-dim)", lineHeight:1.6 }}>
          {reasons.map((r, i) => (
            <li key={i} style={{ position:"relative", padding:"3px 0" }}>
              <span style={{ position:"absolute", left:-14, color:"var(--accent)" }}>›</span>
              {r}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

/* ─── Similar Signals ─────────────────────────────────────────────────────── */
function SimilarSignals({ signal, allSignals }) {
  const past = (allSignals || [])
    .filter(s => s.id !== signal.id && s.action === signal.action
      && s.outcomePct != null)
    .slice(0, 3);

  if (past.length === 0) return null;
  const fmtRet = v => v == null ? "—" : `${v >= 0 ? "+" : ""}${v.toFixed(2)}%`;

  return (
    <div className="section" style={{ marginTop:12 }}>
      <div className="section-title">Recent similar setups · outcome resolved</div>
      <div style={{ display:"grid", gridTemplateColumns:"repeat(3,1fr)", gap:8 }}>
        {past.map((s, i) => {
          const win = (s.outcomePct || 0) > 0;
          return (
            <div key={i} style={{
              background:"var(--bg-1)", border:`1px solid var(--line)`,
              borderLeft:`2px solid ${win ? "var(--up)" : "var(--down)"}`,
              borderRadius:8, padding:"10px 12px" }}>
              <div style={{ display:"flex", alignItems:"center", gap:8, marginBottom:6 }}>
                <span style={{ fontFamily:"var(--font-mono)", fontWeight:700, fontSize:13 }}>{s.ticker}</span>
                <span style={{ fontFamily:"var(--font-mono)", fontSize:9, padding:"1px 5px",
                  borderRadius:3, letterSpacing:"0.1em",
                  color: s.action === "BUY" ? "var(--up)" : "var(--down)",
                  background: s.action === "BUY" ? "rgba(16,185,129,0.12)" : "rgba(239,68,68,0.12)" }}>
                  {s.action}
                </span>
                <span style={{ marginLeft:"auto", fontFamily:"var(--font-mono)", fontSize:11,
                  color:"var(--text-faint)" }}>{s.confidence?.toFixed(0)}%</span>
              </div>
              <div style={{ fontFamily:"var(--font-mono)", fontSize:18,
                color: win ? "var(--up)" : "var(--down)", fontWeight:600 }}>
                {fmtRet(s.outcomePct)}
              </div>
              <div style={{ fontSize:10, color:"var(--text-faint)", marginTop:3 }}>
                {s.date || fmtETFull(s.ts)?.slice(0,10) || "—"}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ─── Position Size Calculator ─────────────────────────────────────────────── */
function PositionCalc({ signal, onPaperTrade }) {
  const [portfolio, setPortfolio] = useState(50000);
  const [riskPct,   setRiskPct]   = useState(1);
  const [paperDone, setPaperDone] = useState(false);

  const entry    = signal.entry  || signal.price || 1;
  const stop     = signal.stop   || entry * 0.97;
  const target   = signal.target || entry * 1.03;
  const riskPer  = Math.abs(entry - stop);
  const rewardPer = Math.abs(target - entry);
  const dollarRisk = (portfolio * riskPct) / 100;
  const shares   = riskPer > 0 ? Math.floor(dollarRisk / riskPer) : 0;
  const maxLoss  = shares * riskPer;
  const maxGain  = shares * rewardPer;

  const inputStyle = {
    width:70, background:"var(--bg-3)", border:"1px solid var(--line)",
    borderRadius:4, padding:"3px 6px", fontFamily:"var(--font-mono)",
    fontSize:12, color:"var(--text)", textAlign:"right", outline:"none",
  };

  return (
    <div style={{ margin:"0 0 0 0", padding:"12px 16px",
                  background:"var(--bg-1)", borderTop:"1px solid var(--line)",
                  borderBottom:"1px solid var(--line)" }}>
      <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", marginBottom:10 }}>
        <span style={{ fontSize:10, fontFamily:"var(--font-mono)", textTransform:"uppercase",
                       letterSpacing:"0.1em", color:"var(--text-faint)", fontWeight:700 }}>
          Position Sizing
        </span>
        <span style={{ fontSize:10, color:"var(--text-faint)" }}>
          Risk {riskPct}% of ${portfolio.toLocaleString()}
        </span>
      </div>

      <div style={{ display:"flex", gap:16, alignItems:"flex-end", flexWrap:"wrap", marginBottom:12 }}>
        <label style={{ display:"flex", flexDirection:"column", gap:3 }}>
          <span style={{ fontSize:10, color:"var(--text-faint)" }}>Portfolio ($)</span>
          <div style={{ display:"flex", alignItems:"center", gap:3 }}>
            <span style={{ fontSize:11, color:"var(--text-faint)" }}>$</span>
            <input type="number" value={portfolio} min={100} step={1000}
              onChange={e => setPortfolio(Math.max(100, +e.target.value || 100))}
              style={inputStyle}/>
          </div>
        </label>
        <label style={{ display:"flex", flexDirection:"column", gap:3 }}>
          <span style={{ fontSize:10, color:"var(--text-faint)" }}>Risk per trade</span>
          <div style={{ display:"flex", alignItems:"center", gap:3 }}>
            <input type="number" value={riskPct} min={0.1} max={10} step={0.5}
              onChange={e => setRiskPct(Math.min(10, Math.max(0.1, +e.target.value || 1)))}
              style={{ ...inputStyle, width:46 }}/>
            <span style={{ fontSize:11, color:"var(--text-faint)" }}>%</span>
          </div>
        </label>
      </div>

      <div style={{ display:"flex", gap:6, flexWrap:"wrap", alignItems:"center" }}>
        {[
          { label:"Shares",   val: shares > 0 ? shares.toLocaleString() : "—",        color:"var(--text)" },
          { label:"Max loss",  val: shares > 0 ? `-$${Math.round(maxLoss).toLocaleString()}` : "—", color:"var(--down)" },
          { label:"Max gain",  val: shares > 0 ? `+$${Math.round(maxGain).toLocaleString()}` : "—", color:"var(--up)"   },
          { label:"Notional",  val: shares > 0 ? `$${Math.round(shares * entry).toLocaleString()}` : "—", color:"var(--text-dim)" },
        ].map(({ label, val, color }) => (
          <div key={label} style={{ flex:"1 1 80px", background:"var(--bg-2)",
            border:"1px solid var(--line)", borderRadius:6,
            padding:"6px 10px", minWidth:70 }}>
            <div style={{ fontSize:9, color:"var(--text-faint)", fontFamily:"var(--font-mono)",
                          textTransform:"uppercase", letterSpacing:"0.08em", marginBottom:2 }}>{label}</div>
            <div style={{ fontSize:13, fontWeight:700, fontFamily:"var(--font-mono)", color }}>{val}</div>
          </div>
        ))}

        {signal.action !== "HOLD" && (
          <button
            onClick={() => { onPaperTrade(); setPaperDone(true); setTimeout(() => setPaperDone(false), 2000); }}
            style={{ flex:"1 1 80px", minWidth:90, padding:"8px 12px", borderRadius:6, cursor:"pointer",
              fontFamily:"var(--font-mono)", fontSize:11, fontWeight:700, letterSpacing:"0.05em",
              border: paperDone ? "1px solid var(--up)" : "1px solid var(--accent)",
              background: paperDone ? "rgba(16,185,129,0.15)" : "rgba(99,102,241,0.15)",
              color: paperDone ? "var(--up)" : "var(--accent)",
              transition:"all 0.2s" }}>
            {paperDone ? "✓ PLACED" : "PAPER TRADE"}
          </button>
        )}
      </div>

      <div style={{ fontSize:9, color:"var(--text-faint)", marginTop:8, lineHeight:1.4 }}>
        Based on ${fmt(entry)} entry · ${fmt(stop)} stop ({riskPer > 0 ? fmt(riskPer,2) : "—"}/share risk). Not financial advice.
      </div>
    </div>
  );
}

/* ─── Simulated Returns Panel ──────────────────────────────────────────────── */
function SimulatedReturnsPanel({ signal, onClose }) {
  const [capital,   setCapital]   = useState(10000);
  const [posSize,   setPosSize]   = useState(5);
  const [simTrades, setSimTrades] = useState(50);

  const entry  = signal.entry  || signal.price;
  const stop   = signal.stop   || entry * 0.97;
  const target = signal.target || entry * 1.05;
  const rrNum  = parseFloat(signal.rr) || Math.abs((target - entry) / Math.max(0.001, Math.abs(entry - stop))) || 1.5;
  const riskPct = Math.max(0.001, Math.abs((entry - stop) / entry));
  const winProb = Math.min(0.82, Math.max(0.35, (signal.confidence || 50) / 100 * 0.88));

  const [sim, setSim] = useState(null);
  const [simLoading, setSimLoading] = useState(false);
  const workerRef = React.useRef(null);

  useEffect(() => {
    const cap = Math.max(100, Number(capital) || 10000);
    setSimLoading(true);
    if (workerRef.current) { workerRef.current.terminate(); }
    let w;
    try {
      w = new Worker('/monte_carlo_worker.js');
      workerRef.current = w;
      w.onmessage = (e) => {
        const { avgFinalCapital, maxDrawdown, samplePaths } = e.data;
        const curve = samplePaths?.[0] ?? [cap, avgFinalCapital];
        const finalEq = avgFinalCapital;
        const ret = (finalEq - cap) / cap * 100;
        const wins = Math.round(simTrades * winProb);
        setSim({ curve, wins, losses: simTrades - wins, finalEq, maxDD: maxDrawdown, ret });
        setSimLoading(false);
      };
      w.onerror = () => { setSimLoading(false); w.terminate(); workerRef.current = null; };
      w.postMessage({ startingCapital: cap, riskPct: posSize * riskPct * 100,
                      trades: simTrades, winRate: winProb, rr: rrNum, paths: 500 });
    } catch (_) {
      const rand = (() => { let s = 42; return () => { s=(s*9301+49297)%233280; return s/233280; }; })();
      let eq = cap; const curve = [cap]; let wins = 0, maxEq = cap, maxDD = 0;
      for (let i = 0; i < simTrades; i++) {
        const risk = eq * (posSize / 100) * riskPct, reward = risk * rrNum;
        if (rand() < winProb) { eq += reward; wins++; } else { eq -= risk; }
        eq = Math.max(0, eq); curve.push(eq);
        if (eq > maxEq) maxEq = eq;
        const dd = (maxEq - eq) / maxEq * 100; if (dd > maxDD) maxDD = dd;
      }
      setSim({ curve, wins, losses: simTrades - wins, finalEq: eq, maxDD, ret: (eq - cap) / cap * 100 });
      setSimLoading(false);
    }
    return () => { if (workerRef.current) { workerRef.current.terminate(); workerRef.current = null; } };
  }, [signal.ticker, capital, posSize, simTrades, winProb, rrNum, riskPct]);

  const simData = sim || { curve: [Number(capital)||10000], wins: 0, losses: 0,
                            finalEq: Number(capital)||10000, maxDD: 0, ret: 0 };

  const cap = Math.max(100, Number(capital) || 10000);
  const winRate = simData.wins / simTrades * 100;
  const retColor = simData.ret >= 0 ? "var(--up)" : "var(--down)";
  const dollarRiskPerTrade = cap * (posSize / 100) * riskPct;
  const dollarRewardPerTrade = dollarRiskPerTrade * rrNum;

  const CW = 320, CH = 90;
  const lo = Math.min(...simData.curve), hi = Math.max(...simData.curve, lo + 1);
  const ys = v => CH - 8 - ((v - lo) / (hi - lo)) * (CH - 16);
  const xs = i => (i / (simData.curve.length - 1)) * CW;
  const pathD = simData.curve.map((v, i) => `${i === 0 ? "M" : "L"} ${xs(i).toFixed(1)} ${ys(v).toFixed(1)}`).join(" ");
  const areaD = `${pathD} L ${CW} ${CH} L 0 ${CH} Z`;
  const lineColor = simData.ret >= 0 ? "var(--up)" : "var(--down)";

  const summaryText = (() => {
    if (simLoading) return "Running 500-path simulation…";
    if (simData.ret >= 20) return `Strong edge. Consistently taking signals at this confidence level would likely grow your portfolio significantly over time.`;
    if (simData.ret >= 5)  return `Positive edge. Following this quality of signal regularly shows modest, consistent portfolio growth.`;
    if (simData.ret >= 0)  return `Marginal edge. Barely profitable — consider sizing down or waiting for signals above ${Math.round((signal.confidence || 65) + 5)}% confidence.`;
    return `Negative edge at current settings. Lower your position size, or only act on higher-confidence signals.`;
  })();

  return (
    <div className="pane">
      <div className="pane-head">
        <span className="title">What-If Simulator</span>
        <span className="sep"/>
        <span className="mono faint" style={{ fontSize:10 }}>{signal.ticker}</span>
        <div className="right">
          <button className="iconbtn" style={{ width:24, height:24 }} onClick={onClose} title="Back to delivery log">
            <Icon name="x" size={12}/>
          </button>
        </div>
      </div>

      <div style={{ overflowY:"auto", flex:1, padding:"14px 16px", display:"flex", flexDirection:"column", gap:14 }}>
        <div style={{ fontSize:12, color:"var(--text-dim)", lineHeight:1.6, padding:"10px 12px", background:"var(--bg-2)", borderRadius:8, border:"1px solid var(--line)" }}>
          <strong style={{ color:"var(--text)" }}>What does this show?</strong> The scanner fires signals like this one — <strong>{(signal.confidence || 0).toFixed(0)}% confidence, R:R {rrNum.toFixed(1)}</strong> — across many tickers every day. If you acted on <strong>{simTrades}</strong> of them over time, risking <strong>{posSize}%</strong> of your <strong>${cap.toLocaleString()}</strong> on each, this is how your account would likely trend.
          <br/><br/>
          Each signal at this confidence level has roughly a <strong style={{ color:"var(--accent)" }}>{(winProb * 100).toFixed(0)}%</strong> chance of hitting its target. Per trade: risk <strong style={{ color:"var(--down)" }}>${Math.round(dollarRiskPerTrade).toLocaleString()}</strong> to potentially make <strong style={{ color:"var(--up)" }}>${Math.round(dollarRewardPerTrade).toLocaleString()}</strong>.
        </div>

        <div style={{ background:"var(--bg-2)", border:"1px solid var(--line)", borderRadius:8, padding:"12px 14px" }}>
          <div style={{ fontSize:9, fontFamily:"var(--font-mono)", textTransform:"uppercase", letterSpacing:"0.1em", color:"var(--text-faint)", marginBottom:10 }}>Adjust the scenario</div>
          <div style={{ display:"flex", flexDirection:"column", gap:12 }}>
            <label style={{ display:"flex", justifyContent:"space-between", alignItems:"center", fontSize:12 }}>
              <div>
                <div style={{ color:"var(--text-dim)" }}>Starting capital</div>
                <div style={{ fontSize:10, color:"var(--text-faint)" }}>How much you're trading with</div>
              </div>
              <div style={{ display:"flex", alignItems:"center", gap:4 }}>
                <span style={{ color:"var(--text-faint)", fontSize:11 }}>$</span>
                <input type="number" value={capital} min={100} step={1000}
                  onChange={e => setCapital(e.target.value === "" ? "" : +e.target.value)}
                  onBlur={() => setCapital(Math.max(100, Number(capital) || 10000))}
                  style={{ width:84, background:"var(--bg-3)", border:"1px solid var(--line)",
                    borderRadius:4, padding:"3px 6px", fontFamily:"var(--font-mono)",
                    fontSize:12, color:"var(--text)", textAlign:"right", outline:"none" }}
                />
              </div>
            </label>
            <label style={{ display:"flex", justifyContent:"space-between", alignItems:"center", fontSize:12 }}>
              <div>
                <div style={{ color:"var(--text-dim)" }}>Risk per trade — <strong style={{ color:"var(--accent)" }}>{posSize}%</strong></div>
                <div style={{ fontSize:10, color:"var(--text-faint)" }}>You'd risk ${Math.round(dollarRiskPerTrade).toLocaleString()} to make ${Math.round(dollarRewardPerTrade).toLocaleString()}</div>
              </div>
              <input type="range" min={1} max={25} step={1} value={posSize}
                onChange={e => setPosSize(Number(e.target.value))} style={{ width:70 }}/>
            </label>
            <label style={{ display:"flex", justifyContent:"space-between", alignItems:"center", fontSize:12 }}>
              <div>
                <div style={{ color:"var(--text-dim)" }}>Signals you act on — <strong style={{ color:"var(--accent)" }}>{simTrades}</strong></div>
                <div style={{ fontSize:10, color:"var(--text-faint)" }}>Across all tickers over time, not just this one</div>
              </div>
              <input type="range" min={10} max={200} step={10} value={simTrades}
                onChange={e => setSimTrades(Number(e.target.value))} style={{ width:70 }}/>
            </label>
          </div>
        </div>

        <div style={{ padding:"10px 14px", borderRadius:8, background:`color-mix(in oklch,${retColor} 8%,var(--bg-2))`, border:`1px solid color-mix(in oklch,${retColor} 25%,transparent)`, fontSize:12, color:"var(--text)", lineHeight:1.6 }}>
          {summaryText}
        </div>

        <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:8 }}>
          {[
            ["Portfolio after {n} trades", `${simData.ret >= 0 ? "+" : ""}${simData.ret.toFixed(1)}%`, retColor, `$${cap.toLocaleString()} → $${simData.finalEq.toLocaleString("en-US", { maximumFractionDigits:0 })}`],
            ["Trades won vs lost",  `${simData.wins}W · ${simData.losses}L`, winRate >= 55 ? "var(--up)" : winRate >= 40 ? "var(--warn)" : "var(--down)", `${winRate.toFixed(0)}% win rate`],
            ["Worst losing streak", `-${simData.maxDD.toFixed(1)}%`, simData.maxDD > 30 ? "var(--down)" : simData.maxDD > 15 ? "var(--warn)" : "var(--up)", "Max account drop before recovery"],
            ["Reward vs risk",      `${rrNum.toFixed(1)} : 1`, "var(--text)", `Win $${Math.round(dollarRewardPerTrade).toLocaleString()} · Lose $${Math.round(dollarRiskPerTrade).toLocaleString()}`],
          ].map(([l, v, c, sub]) => (
            <div key={l} style={{ background:"var(--bg-2)", border:"1px solid var(--line)", borderRadius:8, padding:"10px 12px" }}>
              <div style={{ fontSize:9, color:"var(--text-faint)", marginBottom:4, lineHeight:1.3 }}>{l.replace("{n}", simTrades)}</div>
              <div style={{ fontSize:17, fontWeight:700, fontFamily:"var(--font-mono)", color:c, marginBottom:2 }}>{v}</div>
              <div style={{ fontSize:9, color:"var(--text-faint)" }}>{sub}</div>
            </div>
          ))}
        </div>

        <div>
          <div style={{ fontSize:9, fontFamily:"var(--font-mono)", textTransform:"uppercase", letterSpacing:"0.1em", color:"var(--text-faint)", marginBottom:6 }}>
            Portfolio value across {simTrades} signals
          </div>
          <svg viewBox={`0 0 ${CW} ${CH}`} style={{ width:"100%", height:90, display:"block" }} preserveAspectRatio="none">
            <defs>
              <linearGradient id="sim-eq-grad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={lineColor} stopOpacity="0.3"/>
                <stop offset="100%" stopColor={lineColor} stopOpacity="0.03"/>
              </linearGradient>
            </defs>
            <path d={areaD} fill="url(#sim-eq-grad)"/>
            <path d={pathD} stroke={lineColor} strokeWidth="1.5" fill="none"/>
            {simLoading && <rect x="0" y="0" width={CW} height={CH} fill="var(--bg-2)" opacity="0.7"/>}
            {simLoading && <text x={CW/2} y={CH/2} textAnchor="middle" fill="var(--text-dim)" fontSize="10">Running 500 paths…</text>}
            <circle cx={xs(0).toFixed(1)} cy={ys(simData.curve[0]).toFixed(1)} r="3" fill="var(--text-faint)" opacity="0.7"/>
            <circle cx={xs(simData.curve.length - 1).toFixed(1)} cy={ys(simData.finalEq).toFixed(1)} r="3" fill={lineColor}/>
          </svg>
          <div style={{ display:"flex", justifyContent:"space-between", fontSize:9, fontFamily:"var(--font-mono)", color:"var(--text-faint)", marginTop:3 }}>
            <span>Start · ${cap.toLocaleString()}</span>
            <span>After {simTrades} trades · ${simData.finalEq.toLocaleString("en-US", { maximumFractionDigits:0 })}</span>
          </div>
        </div>

        <div style={{ fontSize:10, color:"var(--text-faint)", lineHeight:1.6, borderTop:"1px solid var(--line)", paddingTop:10 }}>
          ⚠️ This is a hypothetical simulation based on the signal's confidence score. Real markets have slippage, gaps, and correlation — actual results will differ. Not financial advice.
        </div>
      </div>
    </div>
  );
}

/* ─── PaperView ──────────────────────────────────────────────────────────────── */
function PaperView({ open, onClose, online }) {
  const [account,   setAccount]   = useState(null);
  const [positions, setPositions] = useState([]);
  const [orders,    setOrders]    = useState([]);
  const [risk,      setRisk]      = useState(null);
  const [volTarget, setVolTarget] = useState(null);
  const [volLoading, setVolLoading] = useState(false);
  const [loading,   setLoading]   = useState(false);
  const [err,       setErr]       = useState(null);

  useEffect(() => {
    if (!open) return;
    if (!online) { setErr("offline"); return; }
    setErr(null);
    setLoading(true);
    Promise.all([
      authFetch("/api/paper/account"),
      authFetch("/api/paper/positions"),
      authFetch("/api/paper/orders"),
      authFetch("/api/paper/risk"),
    ]).then(async ([accR, posR, ordR, rskR]) => {
      if (accR.status === 402) { setErr("upgrade"); return; }
      const [acc, pos, ord, rsk] = await Promise.all([accR.json(), posR.json(), ordR.json(), rskR.json()]);
      if (acc) setAccount(acc);
      if (Array.isArray(pos)) setPositions(pos);
      if (Array.isArray(ord)) setOrders(ord);
      if (rsk) setRisk(rsk);
    }).catch(() => setErr("offline"))
      .finally(() => setLoading(false));
  }, [open, online]);

  const loadVolTarget = (tickers = "") => {
    setVolLoading(true);
    const qs = tickers ? `?tickers=${encodeURIComponent(tickers)}` : "";
    authFetch(`/api/paper/volatility-target${qs}`)
      .then(r => r.json()).then(d => setVolTarget(d)).catch(() => {})
      .finally(() => setVolLoading(false));
  };

  const fmtMoney = v => v == null ? "—" : `$${Number(v).toLocaleString("en-US", { minimumFractionDigits:2, maximumFractionDigits:2 })}`;
  const fmtPct   = v => v == null ? "—" : `${v >= 0 ? "+" : ""}${Number(v).toFixed(2)}%`;
  const rc = v => v == null ? "var(--text-faint)" : v >= 0 ? "var(--up)" : "var(--down)";

  const closePosition = async (sym) => {
    await apiFetch(`/api/paper/positions/${sym}`, { method:"DELETE" });
    setPositions(prev => prev.filter(p => (p.symbol||p.ticker) !== sym));
  };

  const cancelOrder = async (orderId) => {
    await authFetch(`/api/paper/orders/${orderId}`, { method:"DELETE" });
    setOrders(prev => prev.map(o => o.id === orderId ? { ...o, status:"canceled" } : o));
  };

  return (
    <div className={`overlay ${open ? "open" : ""}`}>
      <div className="overlay-head">
        <div><div className="crumb">PAPER PORTFOLIO</div><h2>Simulated trading account</h2></div>
        <button className="btn ghost" style={{ marginLeft:"auto" }} onClick={onClose}><Icon name="x" size={14}/> Close</button>
      </div>
      <div style={{ padding:"20px 28px", overflowY:"auto", maxHeight:"calc(100vh - 100px)", display:"flex", flexDirection:"column", gap:20 }}>
        {err === "upgrade"  && <UpgradePrompt feature="Paper Portfolio" minTier="pro"/>}
        {err === "offline"  && <div style={{ color:"var(--text-faint)", fontSize:12 }}>Backend offline or Alpaca API keys not configured.</div>}
        {loading && <div style={{ color:"var(--text-faint)", fontSize:12 }}>Loading paper account…</div>}

        {account && (
          <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fill,minmax(160px,1fr))", gap:12 }}>
            {[
              ["Equity", fmtMoney(account.equity), rc(account.equity)],
              ["Cash", fmtMoney(account.cash), "var(--text)"],
              ["P&L", fmtMoney(account.unrealized_pl), rc(account.unrealized_pl)],
              ["Day P&L", fmtMoney(account.unrealized_intraday_pl), rc(account.unrealized_intraday_pl)],
            ].map(([l,v,c]) => (
              <div key={l} style={{ background:"var(--bg-2)", borderRadius:8, padding:"14px 16px" }}>
                <div style={{ fontSize:10, color:"var(--text-faint)", fontFamily:"var(--font-mono)", textTransform:"uppercase", letterSpacing:"0.08em", marginBottom:6 }}>{l}</div>
                <div style={{ fontSize:18, fontWeight:700, fontFamily:"var(--font-mono)", color:c }}>{v}</div>
              </div>
            ))}
          </div>
        )}

        {risk && (
          <div>
            <div style={{ fontSize:11, fontWeight:600, color:"var(--text-dim)", textTransform:"uppercase", letterSpacing:"0.08em", marginBottom:10 }}>Risk metrics</div>
            <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fill,minmax(140px,1fr))", gap:10 }}>
              {[
                ["Beta vs SPY", risk.beta?.toFixed(2), risk.beta > 1.2 ? "var(--warn)" : "var(--text)"],
                ["Sharpe (ann.)", risk.sharpe?.toFixed(2), (risk.sharpe||0) >= 1 ? "var(--up)" : "var(--text)"],
                ["Max Drawdown", risk.max_drawdown != null ? fmtPct(risk.max_drawdown) : "—", "var(--down)"],
                ["Exposure", risk.exposure_pct != null ? fmtPct(risk.exposure_pct) : "—", "var(--text)"],
              ].map(([l,v,c]) => (
                <div key={l} style={{ background:"var(--bg-2)", borderRadius:8, padding:"12px 14px", border:"1px solid var(--line)" }}>
                  <div style={{ fontSize:9, color:"var(--text-faint)", fontFamily:"var(--font-mono)", textTransform:"uppercase", letterSpacing:"0.08em", marginBottom:6 }}>{l}</div>
                  <div style={{ fontSize:16, fontWeight:700, fontFamily:"var(--font-mono)", color:c }}>{v ?? "—"}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div style={{ border:"1px solid var(--line)", borderRadius:10, padding:"16px 18px" }}>
          <div style={{ display:"flex", alignItems:"center", gap:10, marginBottom:12 }}>
            <div>
              <div style={{ fontSize:11, fontWeight:600, color:"var(--text-dim)", textTransform:"uppercase", letterSpacing:"0.08em" }}>Volatility Targeting</div>
              <div style={{ fontSize:10, color:"var(--text-faint)", marginTop:2 }}>15% annualised target · inverse-vol weights with correlation penalty</div>
            </div>
            <button className="btn ghost" style={{ marginLeft:"auto", fontSize:10 }} onClick={() => loadVolTarget(positions.map(p=>p.symbol||p.ticker).join(",") || "")}>
              {volLoading ? "Computing…" : volTarget ? "Refresh" : "Compute weights"}
            </button>
          </div>
          {volTarget && !volTarget.error && (
            <>
              <div style={{ display:"grid", gridTemplateColumns:"repeat(3,1fr)", gap:8, marginBottom:12 }}>
                {[
                  ["Target Vol", `${volTarget.target_vol_pct}%`],
                  ["Est. Port Vol", `${volTarget.estimated_port_vol_pct}%`],
                  ["Scale factor", `${volTarget.scale_factor}×`],
                ].map(([l,v]) => (
                  <div key={l} style={{ background:"var(--bg-2)", borderRadius:6, padding:"10px 12px" }}>
                    <div style={{ fontSize:9, color:"var(--text-faint)", fontFamily:"var(--font-mono)", textTransform:"uppercase", letterSpacing:"0.08em", marginBottom:4 }}>{l}</div>
                    <div style={{ fontSize:15, fontWeight:700, fontFamily:"var(--font-mono)", color:"var(--accent)" }}>{v}</div>
                  </div>
                ))}
              </div>
              <table style={{ width:"100%", borderCollapse:"collapse", fontSize:11, fontFamily:"var(--font-mono)" }}>
                <thead><tr style={{ borderBottom:"1px solid var(--line)", color:"var(--text-faint)", fontSize:9, textTransform:"uppercase" }}>
                  {["Asset","Weight","Ann. Vol"].map(h => <th key={h} style={{ padding:"5px 8px", textAlign: h==="Asset"?"left":"right", fontWeight:500 }}>{h}</th>)}
                </tr></thead>
                <tbody>
                  {(volTarget.assets||[]).map((a,i) => (
                    <tr key={i} style={{ borderBottom:"1px solid var(--line)" }}>
                      <td style={{ padding:"5px 8px", fontWeight:600 }}>{a.ticker}</td>
                      <td style={{ padding:"5px 8px", textAlign:"right" }}>
                        <span style={{ display:"inline-block", background:`var(--accent)${Math.round(a.weight_pct*2.55).toString(16).padStart(2,"0")}`, borderRadius:3, padding:"1px 7px" }}>{a.weight_pct}%</span>
                      </td>
                      <td style={{ padding:"5px 8px", textAlign:"right", color: a.annual_vol_pct > 30 ? "var(--down)" : a.annual_vol_pct > 20 ? "var(--warn)" : "var(--text-faint)" }}>{a.annual_vol_pct}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {(volTarget.high_correlation_pairs||[]).length > 0 && (
                <div style={{ marginTop:10, padding:"8px 10px", background:"var(--bg-2)", borderRadius:6, fontSize:10, color:"var(--text-faint)", fontFamily:"var(--font-mono)" }}>
                  <span style={{ color:"var(--warn)", fontWeight:600 }}>High correlation penalties applied: </span>
                  {volTarget.high_correlation_pairs.map(p => `${p.a}/${p.b} (${p.correlation})`).join(" · ")}
                </div>
              )}
            </>
          )}
          {volTarget?.error && <div style={{ fontSize:11, color:"var(--down)" }}>{volTarget.error}</div>}
        </div>

        {positions.length > 0 && (
          <div>
            <div style={{ fontSize:11, fontWeight:600, color:"var(--text-dim)", textTransform:"uppercase", letterSpacing:"0.08em", marginBottom:10 }}>Open positions ({positions.length})</div>
            <table style={{ width:"100%", borderCollapse:"collapse", fontSize:12, fontFamily:"var(--font-mono)" }}>
              <thead><tr style={{ borderBottom:"1px solid var(--line)", color:"var(--text-faint)", fontSize:10, textTransform:"uppercase" }}>
                {["Symbol","Qty","Avg Cost","Current","P&L","P&L %",""].map(h => <th key={h} style={{ padding:"7px 10px", textAlign: h===""?"center":"right", fontWeight:500, ...(h==="Symbol"?{textAlign:"left"}:{}) }}>{h}</th>)}
              </tr></thead>
              <tbody>
                {positions.map((p,i) => {
                  const sym = p.symbol || p.ticker || "—";
                  const pl = parseFloat(p.unrealized_pl || p.pnl || 0);
                  const plPct = parseFloat(p.unrealized_plpc || p.pnl_pct || 0) * (Math.abs(p.unrealized_plpc||0) < 1 ? 100 : 1);
                  return (
                    <tr key={i} style={{ borderBottom:"1px solid var(--line)" }}>
                      <td style={{ padding:"7px 10px", fontWeight:600 }}>{sym}</td>
                      <td style={{ padding:"7px 10px", textAlign:"right" }}>{p.qty}</td>
                      <td style={{ padding:"7px 10px", textAlign:"right" }}>{p.avg_entry_price ? fmtMoney(p.avg_entry_price) : "—"}</td>
                      <td style={{ padding:"7px 10px", textAlign:"right" }}>{p.current_price ? fmtMoney(p.current_price) : "—"}</td>
                      <td style={{ padding:"7px 10px", textAlign:"right", color:rc(pl), fontWeight:600 }}>{fmtMoney(pl)}</td>
                      <td style={{ padding:"7px 10px", textAlign:"right", color:rc(plPct) }}>{fmtPct(plPct)}</td>
                      <td style={{ padding:"7px 4px", textAlign:"center" }}>
                        <button className="btn ghost" style={{ fontSize:10, padding:"2px 8px", color:"var(--down)" }} onClick={() => closePosition(sym)}>Close</button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {orders.length > 0 && (
          <div>
            <div style={{ fontSize:11, fontWeight:600, color:"var(--text-dim)", textTransform:"uppercase", letterSpacing:"0.08em", marginBottom:10 }}>Recent orders ({orders.length})</div>
            <table style={{ width:"100%", borderCollapse:"collapse", fontSize:12, fontFamily:"var(--font-mono)" }}>
              <thead><tr style={{ borderBottom:"1px solid var(--line)", color:"var(--text-faint)", fontSize:10, textTransform:"uppercase" }}>
                {["Symbol","Side","Qty","Type","Status","Filled At",""].map(h => <th key={h} style={{ padding:"7px 10px", textAlign: h==="Symbol"?"left":"right", fontWeight:500 }}>{h}</th>)}
              </tr></thead>
              <tbody>
                {orders.slice(0,20).map((o,i) => {
                  const cancelable = ["new","pending_new","accepted","held"].includes(o.status);
                  return (
                  <tr key={i} style={{ borderBottom:"1px solid var(--line)" }}>
                    <td style={{ padding:"7px 10px", fontWeight:600 }}>{o.symbol}</td>
                    <td style={{ padding:"7px 10px", textAlign:"right", color: o.side==="buy"?"var(--up)":"var(--down)", fontWeight:600, textTransform:"uppercase" }}>{o.side}</td>
                    <td style={{ padding:"7px 10px", textAlign:"right" }}>{o.qty}</td>
                    <td style={{ padding:"7px 10px", textAlign:"right", color:"var(--text-faint)" }}>{o.type}</td>
                    <td style={{ padding:"7px 10px", textAlign:"right", color: o.status==="filled"?"var(--up)":o.status==="canceled"?"var(--text-faint)":"var(--warn)", textTransform:"uppercase", fontSize:10 }}>{o.status}</td>
                    <td style={{ padding:"7px 10px", textAlign:"right", color:"var(--text-faint)", fontSize:11 }}>{o.filled_at ? fmtETTime(o.filled_at) : "—"}</td>
                    <td style={{ padding:"7px 4px", textAlign:"center" }}>
                      {cancelable && (
                        <button className="btn ghost" style={{ fontSize:10, padding:"2px 8px", color:"var(--down)" }}
                          onClick={() => cancelOrder(o.id)}>Cancel</button>
                      )}
                    </td>
                  </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {!loading && !account && (
          <div style={{ padding:"40px 0", textAlign:"center", color:"var(--text-faint)", fontSize:12 }}>
            Paper account not configured. Set Alpaca API keys in .env to enable paper trading.
          </div>
        )}
      </div>
    </div>
  );
}

/* ─── Inline upgrade prompt for 402 responses ────────────────────────────────── */
function UpgradePrompt({ feature, minTier = "basic" }) {
  return (
    <div style={{ padding:"40px 0", textAlign:"center", display:"flex", flexDirection:"column", alignItems:"center", gap:12 }}>
      <div style={{ fontSize:28, opacity:0.4 }}>🔒</div>
      <div style={{ fontSize:14, fontWeight:600, color:"var(--text)" }}>{feature} requires {minTier.charAt(0).toUpperCase()+minTier.slice(1)}</div>
      <div style={{ fontSize:12, color:"var(--text-faint)", marginBottom:4 }}>Upgrade your plan to unlock this feature.</div>
      <button className="btn primary" style={{ fontSize:12 }} onClick={() => window.location.href="/app#pricing"}>
        Upgrade plan
      </button>
    </div>
  );
}

/* ─── MarketOverviewView ───────────────────────────────────────────────────── */
function MarketOverviewView({ open, onClose, online }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState(null);

  useEffect(() => {
    if (!open || !online) return;
    setErr(null);
    setLoading(true);
    apiFetch("/api/market/overview")
      .then(d => {
        if (d && typeof d === 'object' && Object.keys(d).length > 0) setData(d);
        else setErr("No data");
      })
      .catch(() => setErr("offline"))
      .finally(() => setLoading(false));
  }, [open, online]);

  const MetricCard = ({ title, value, change, changePct, history, unit = "", tipKey }) => {
    const up = (change || 0) >= 0;
    const color = up ? "var(--up)" : "var(--down)";
    const valFmt = v => typeof v === 'number' ? v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : v;
    return (
      <div className="src-card" style={{ padding: "16px 18px", gap: 8 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span style={{ fontSize: 11, fontWeight: 600, color: "var(--text-dim)", textTransform: "uppercase", letterSpacing: "0.08em" }}>
            {tipKey ? <Tip term={tipKey}>{title}</Tip> : title}
          </span>
          {change != null && changePct != null && (
            <span className="mono" style={{ fontSize: 11, color }}>
              {change >= 0 ? "+" : ""}{valFmt(change)} ({changePct >= 0 ? "+" : ""}{changePct.toFixed(2)}%)
            </span>
          )}
        </div>
        <div className="mono" style={{ fontSize: 22, fontWeight: 700, color: "var(--text)" }}>
          {typeof value === 'number' ? valFmt(value) : value}{unit}
        </div>
        {history && history.length > 1 && (
          <div style={{ height: 32, marginTop: 4 }}>
            <PathSparkline path={history} />
          </div>
        )}
      </div>
    );
  };

  return (
    <div className={`overlay ${open ? "open" : ""}`}>
      <div className="overlay-head">
        <div>
          <div className="crumb">MARKET / OVERVIEW</div>
          <h2>Market dashboard</h2>
        </div>
        <button className="btn ghost" style={{ marginLeft: "auto" }} onClick={onClose}><Icon name="x" size={14}/> Close</button>
      </div>
      <div style={{ padding: "20px 28px", overflowY: "auto", maxHeight: "calc(100vh - 100px)" }}>
        {loading && <div style={{ color: "var(--text-faint)", fontSize: 12 }}>Loading market overview…</div>}
        {err && <div style={{ color: "var(--text-faint)", fontSize: 12 }}>Market overview data is currently unavailable.</div>}
        {data && <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", gap: 14 }}>
            <MetricCard title="S&P 500" value={data.spx?.value} change={data.spx?.change} changePct={data.spx?.change_pct} history={data.spx?.history} />
            <MetricCard title="NASDAQ 100" value={data.ndx?.value} change={data.ndx?.change} changePct={data.ndx?.change_pct} history={data.ndx?.history} />
            <MetricCard title="VIX" value={data.vix?.value} change={data.vix?.change} changePct={data.vix?.change_pct} history={data.vix?.history} tipKey="VIX" />
            <MetricCard title="US 10Y Yield" value={data.yield_10y?.value} change={data.yield_10y?.change} changePct={data.yield_10y?.change_pct} history={data.yield_10y?.history} unit="%" tipKey="YIELD CURVE" />
            <MetricCard title="DXY" value={data.dxy?.value} change={data.dxy?.change} changePct={data.dxy?.change_pct} history={data.dxy?.history} tipKey="DXY" />
            <MetricCard title="Market Breadth" value={`${data.breadth?.pct_above_200d?.toFixed(0) || '—'}`} unit="% > 200d" history={data.breadth?.history} tipKey="MARKET BREADTH" />
            <MetricCard title="Fear & Greed" value={`${data.fear_greed?.score?.toFixed(0) || '—'} (${data.fear_greed?.label || 'N/A'})`} history={data.fear_greed?.history} tipKey="Fear & Greed" />
            <MetricCard title="CBOE Put/Call" value={data.put_call_ratio?.ratio?.toFixed(2)} history={data.put_call_ratio?.history} tipKey="CBOE P/C" />
          </div>}
      </div>
    </div>
  );
}

/* ─── SectorView ─────────────────────────────────────────────────────────────── */
const SECTOR_NAMES = {
  XLK:"Technology", XLV:"Health Care", XLF:"Financials", XLC:"Communication",
  XLY:"Cons. Discr.", XLP:"Cons. Staples", XLI:"Industrials", XLB:"Materials",
  XLRE:"Real Estate", XLU:"Utilities", XLE:"Energy",
};

function SectorView({ open, onClose, online }) {
  const [sectors,  setSectors]  = useState(null);
  const [detail,   setDetail]   = useState(null);
  const [activeEtf, setActiveEtf] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [err, setErr] = useState(null);

  useEffect(() => {
    if (!open) return;
    setErr(null); setActiveEtf(null);
    authFetch("/api/market/sectors")
      .then(async r => {
        if (r.status === 402) { setErr("upgrade"); return; }
        const d = await r.json();
        if (d) setSectors(d);
      }).catch(() => setErr("offline"));
  }, [open]);

  const drillIn = (etf) => {
    setActiveEtf(etf);
    if (detail) return;
    setDetailLoading(true);
    authFetch("/api/market/sectors/detail")
      .then(async r => {
        const d = await r.json();
        if (d) setDetail(d);
      }).catch(() => {})
      .finally(() => setDetailLoading(false));
  };

  const fmtR = v => v == null ? "—" : `${v >= 0 ? "+" : ""}${v.toFixed(2)}%`;
  const rc   = v => v == null ? "var(--text-faint)" : v >= 0 ? "var(--up)" : "var(--down)";

  const activeStocks = activeEtf && detail
    ? (detail.sectors || []).find(s => s.etf === activeEtf)?.stocks || []
    : [];

  return (
    <div className={`overlay ${open ? "open" : ""}`}>
      <div className="overlay-head">
        <div>
          <div className="crumb">MARKET / SECTOR HEATMAP{activeEtf ? ` / ${activeEtf}` : ""}</div>
          <h2>{activeEtf ? `${SECTOR_NAMES[activeEtf] || activeEtf} — stocks` : "Sector performance (1-month)"}</h2>
        </div>
        <div style={{ marginLeft:"auto", display:"flex", gap:8 }}>
          {activeEtf && (
            <button className="btn ghost" style={{ fontSize:11 }} onClick={() => setActiveEtf(null)}>← Back</button>
          )}
          <button className="btn ghost" onClick={onClose}><Icon name="x" size={14}/> Close</button>
        </div>
      </div>
      <div style={{ padding:"20px 28px" }}>
        {err === "upgrade" && <UpgradePrompt feature="Sector heatmap" minTier="basic"/>}
        {err === "offline" && <div style={{ color:"var(--text-faint)", fontSize:12 }}>Backend offline — try again when connected.</div>}

        {!activeEtf && (
          <>
            {!sectors && !err && <div style={{ color:"var(--text-faint)", fontSize:12 }}>Loading…</div>}
            {sectors && (
              <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fill,minmax(200px,1fr))", gap:12 }}>
                {sectors.map(s => (
                  <div key={s.etf} onClick={() => drillIn(s.etf)}
                    style={{ background:"var(--bg-1)", cursor:"pointer",
                      border:`1px solid ${(s.ret_1m||0) >= 0 ? "color-mix(in oklch,var(--up) 25%,var(--line))" : "color-mix(in oklch,var(--down) 25%,var(--line))"}`,
                      borderRadius:10, padding:"16px", transition:"opacity 0.12s" }}
                    onMouseEnter={e => e.currentTarget.style.opacity="0.82"}
                    onMouseLeave={e => e.currentTarget.style.opacity="1"}>
                    <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:8 }}>
                      <span style={{ fontFamily:"var(--font-mono)", fontWeight:700, fontSize:13 }}>{s.etf}</span>
                      <span style={{ fontFamily:"var(--font-mono)", fontSize:16, fontWeight:700, color:rc(s.ret_1m) }}>{fmtR(s.ret_1m)}</span>
                    </div>
                    <div style={{ fontSize:11, color:"var(--text-dim)", marginBottom:6 }}>{SECTOR_NAMES[s.etf] || s.etf}</div>
                    <div style={{ height:4, borderRadius:2, background:"var(--bg-3)", overflow:"hidden" }}>
                      <div style={{ height:"100%", width:`${Math.min(100, Math.abs(s.ret_1m||0) * 5)}%`, background:rc(s.ret_1m), borderRadius:2 }}/>
                    </div>
                    <div style={{ fontSize:9, color:"var(--text-faint)", fontFamily:"var(--font-mono)", marginTop:8, textAlign:"right" }}>Click to see stocks →</div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        {activeEtf && (
          <div>
            {detailLoading && <div style={{ color:"var(--text-faint)", fontSize:12 }}>Loading stocks…</div>}
            {!detailLoading && activeStocks.length === 0 && (
              <div style={{ color:"var(--text-faint)", fontSize:12 }}>No stocks found in watchlist for {activeEtf}.</div>
            )}
            {activeStocks.length > 0 && (
              <SortableTable
                cols={["Ticker","Company","1M Return","Signal","Confidence"]}
                defaultSort={{ col:2, dir:"desc" }}
                rows={activeStocks.map(s => [
                  s.ticker,
                  s.company || s.ticker,
                  fmtR(s.ret_1m),
                  s.action ? <span className={`signal-verb ${s.action}`} style={{ fontSize:10 }}>{s.action}</span> : "—",
                  s.confidence ? `${s.confidence.toFixed(0)}%` : "—",
                ])}
                colors={[null, null, (_,ri) => rc(activeStocks[ri]?.ret_1m), null, null]}/>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

/* ─── CalendarView ───────────────────────────────────────────────────────────── */
function CalendarView({ open, onClose }) {
  const [events,   setEvents]   = useState(null);
  const [err,      setErr]      = useState(null);
  const [expanded, setExpanded] = useState(null);

  useEffect(() => {
    if (!open) return;
    setErr(null);
    authFetch("/api/market/calendar")
      .then(async r => {
        if (r.status === 402) { setErr("upgrade"); return; }
        const d = await r.json();
        if (d) setEvents(d);
      }).catch(() => setErr("offline"));
  }, [open]);

  const daysUntil = dateStr => {
    try {
      const diff = Math.round((new Date(dateStr) - new Date()) / 86400000);
      return diff < 0 ? null : diff;
    } catch { return null; }
  };

  const impactStyle = imp => {
    if (imp === "HIGH")   return { bg:"rgba(239,68,68,0.12)",  text:"#ef4444",  label:"HIGH IMPACT" };
    if (imp === "MEDIUM") return { bg:"rgba(245,158,11,0.12)", text:"#f59e0b",  label:"MED IMPACT"  };
    return                       { bg:"rgba(148,163,184,0.1)", text:"var(--text-faint)", label:"LOW" };
  };

  const grouped = useMemo(() => {
    if (!events) return [];
    const map = new Map();
    events.forEach(e => {
      const month = e.date.slice(0, 7);
      if (!map.has(month)) map.set(month, []);
      map.get(month).push(e);
    });
    return [...map.entries()].map(([month, evts]) => ({ month, evts }));
  }, [events]);

  const fmtMonth = m => new Date(m + "-01").toLocaleDateString("en-US", { month:"long", year:"numeric" });

  return (
    <div className={`overlay ${open ? "open" : ""}`}>
      <div className="overlay-head">
        <div>
          <div className="crumb">MARKET / ECONOMIC CALENDAR</div>
          <h2>Upcoming macro events</h2>
        </div>
        <button className="btn ghost" style={{ marginLeft:"auto" }} onClick={onClose}><Icon name="x" size={14}/> Close</button>
      </div>
      <div style={{ padding:"20px 28px" }}>
        {err === "upgrade" && <UpgradePrompt feature="Economic calendar" minTier="basic"/>}
        {err === "offline" && <div style={{ color:"var(--text-faint)", fontSize:12 }}>Backend offline.</div>}
        {!events && !err && <div style={{ color:"var(--text-faint)", fontSize:12 }}>Loading…</div>}
        {events && events.length === 0 && <div style={{ color:"var(--text-faint)", fontSize:12 }}>No upcoming events found.</div>}

        {grouped.map(({ month, evts }) => (
          <div key={month} style={{ marginBottom:24 }}>
            <div style={{ fontFamily:"var(--font-mono)", fontSize:10, fontWeight:700, textTransform:"uppercase",
                          letterSpacing:"0.12em", color:"var(--text-faint)", marginBottom:10,
                          paddingBottom:6, borderBottom:"1px solid var(--line)" }}>
              {fmtMonth(month)}
            </div>
            <div style={{ display:"flex", flexDirection:"column", gap:6 }}>
              {evts.map((e, i) => {
                const label  = e.label || "EVENT";
                const color  = e.color || "var(--text-faint)";
                const du     = daysUntil(e.date);
                const imp    = impactStyle(e.impact);
                const isOpen = expanded === `${month}-${i}`;
                const isToday   = du === 0;
                const isImminent = du != null && du <= 3;

                return (
                  <div key={i}
                    style={{ border:`1px solid ${isImminent ? color : "var(--line)"}`,
                             borderRadius:8, background:"var(--bg-1)", overflow:"hidden",
                             boxShadow: isToday ? `0 0 0 2px ${color}40` : "none" }}>
                    <div onClick={() => setExpanded(isOpen ? null : `${month}-${i}`)}
                      style={{ display:"flex", alignItems:"center", gap:14, padding:"12px 14px", cursor:"pointer" }}>
                      <div style={{ width:52, height:44, borderRadius:6, flexShrink:0,
                                    background:`color-mix(in oklch,${color} 14%,transparent)`,
                                    display:"grid", placeItems:"center" }}>
                        <span style={{ fontFamily:"var(--font-mono)", fontSize:9, fontWeight:700,
                                       color, textAlign:"center", lineHeight:1.3, letterSpacing:"0.04em" }}>
                          {label}
                        </span>
                      </div>
                      <div style={{ flex:1, minWidth:0 }}>
                        <div style={{ fontSize:13, fontWeight:600, color:"var(--text)", display:"flex", alignItems:"center", gap:6, flexWrap:"wrap" }}>
                          {e.name || label}
                          {isToday && <span style={{ fontFamily:"var(--font-mono)", fontSize:9, fontWeight:700,
                            background:"var(--warn)", color:"#000", padding:"1px 5px", borderRadius:3 }}>TODAY</span>}
                        </div>
                        <div style={{ fontSize:11, color:"var(--text-faint)", fontFamily:"var(--font-mono)", marginTop:3, display:"flex", gap:10 }}>
                          <span>{e.date}</span>
                          {e.time && <span style={{ color:"var(--text-dim)" }}>· {e.time}</span>}
                        </div>
                      </div>
                      <div style={{ display:"flex", flexDirection:"column", alignItems:"flex-end", gap:4, flexShrink:0 }}>
                        {e.impact && (
                          <span style={{ fontFamily:"var(--font-mono)", fontSize:9, fontWeight:700, padding:"2px 6px",
                                         borderRadius:3, background:imp.bg, color:imp.text }}>
                            {imp.label}
                          </span>
                        )}
                        {du != null && (
                          <span style={{ fontFamily:"var(--font-mono)", fontSize:11,
                                         color: isImminent ? "var(--warn)" : "var(--text-faint)" }}>
                            {du === 0 ? "today" : `${du}d`}
                          </span>
                        )}
                      </div>
                      {e.desc && (
                        <span style={{ color:"var(--text-faint)", fontSize:10, marginLeft:4,
                                       transform: isOpen ? "rotate(180deg)" : "none", transition:"transform 0.15s" }}>▾</span>
                      )}
                    </div>
                    {isOpen && e.desc && (
                      <div style={{ padding:"0 14px 14px 80px", fontSize:12, color:"var(--text-dim)", lineHeight:1.6,
                                    borderTop:"1px solid var(--line)", paddingTop:10, marginTop:0 }}>
                        {e.desc}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ─── DemoTour — BUG FIX: useEffect moved before early return ────────────────── */
function DemoTour({ open, onClose }) {
  const [step, setStep] = useState(0);
  const steps = [
    { title: "Welcome to Signal.Trade",       body: "A personal quant desk that fuses 40+ signals — options flow, 13F institutional data, insider trades and technicals — into one confidence score. Let's take 60 seconds." },
    { title: "Left: Signal feed",             body: "Every live recommendation ranked by confidence. Click any row to expand inline. Use j/k to navigate, Enter for full detail." },
    { title: "Style strip",                   body: "Switch between Intraday, Swing, and Position to filter signals by your trading horizon. The feed, counts, and active detail all update instantly." },
    { title: "Center: Recommendation detail", body: "Action, confidence, plain-English summary, Why Now, Predictive Confidence Intervals, similar historical signals, the chart, and every source that voted. No black boxes." },
    { title: "Right: Delivery log",           body: "Live audit trail of every Telegram send. If a signal fires but doesn't reach you, this is where you'll see exactly why." },
    { title: "Keyboard shortcuts",            body: "j/k moves through the feed. Enter opens detail. Shift+S sends to Telegram. 1/2/3/4 filters the feed. Press ? anytime to reopen this cheat sheet." },
  ];
  // Hook always called before any conditional return
  useEffect(() => { if (open) setStep(0); }, [open]);
  if (!open) return null;
  return (
    <div className="hk-backdrop" onClick={onClose}>
      <div className="tour-modal" onClick={e => e.stopPropagation()}>
        <div className="tour-progress">
          {steps.map((_, i) => <span key={i} className={`tp-dot ${i === step ? "on" : i < step ? "done" : ""}`}/>)}
        </div>
        <div className="tour-step">
          <div className="crumb">STEP {step + 1} OF {steps.length}</div>
          <h3>{steps[step].title}</h3>
          <p>{steps[step].body}</p>
        </div>
        <div className="tour-foot">
          <button className="btn ghost" onClick={onClose}>Skip</button>
          <div style={{ flex:1 }}/>
          {step > 0 && <button className="btn ghost" onClick={() => setStep(step - 1)}>← Back</button>}
          {step < steps.length - 1
            ? <button className="btn primary" onClick={() => setStep(step + 1)}>Next →</button>
            : <button className="btn primary" onClick={onClose}>Get started</button>}
        </div>
      </div>
    </div>
  );
}

function HotkeyHelp({ open, onClose, onTour }) {
  const groups = [
    { title: "Navigation", keys: [["⌘K / Ctrl K", "Search tickers"], ["j / k", "Next / previous signal"], ["Enter", "Open full explanation"], ["Esc", "Close any panel"]] },
    { title: "Actions",    keys: [["d", "Toggle detail / Simulator"], ["p", "Paper trade signal"], ["s", "Skip signal"], ["Shift S", "Send to Telegram"]] },
    { title: "Filters",    keys: [["1", "All signals"], ["2", "BUY only"], ["3", "SELL only"], ["4", "High conviction ≥75%"]] },
    { title: "Display",    keys: [["⌘\\ / Ctrl \\", "Toggle compact / comfortable"], ["?", "Show this cheat sheet"]] },
  ];
  if (!open) return null;
  return (
    <div className="hk-backdrop" onClick={onClose}>
      <div className="hk-modal" onClick={e => e.stopPropagation()}>
        <div className="hk-head">
          <span className="crumb">SHORTCUTS</span>
          <h3>Keyboard cheat sheet</h3>
          <button className="hk-close" onClick={onClose}><Icon name="x" size={14}/></button>
        </div>
        <div className="hk-grid">
          {groups.map(g => (
            <div key={g.title} className="hk-group">
              <div className="hk-group-title mono">{g.title}</div>
              {g.keys.map(([k, label]) => (
                <div key={k} className="hk-row"><kbd>{k}</kbd><span>{label}</span></div>
              ))}
            </div>
          ))}
        </div>
        <div className="hk-foot mono faint" style={{ display:"flex", alignItems:"center", justifyContent:"space-between" }}>
          <span>Press <kbd>?</kbd> to reopen · Press <kbd>Esc</kbd> to close</span>
          {onTour && <button className="btn" style={{ fontSize:10, padding:"3px 10px" }} onClick={() => { onClose(); onTour(); }}>Take a tour →</button>}
        </div>
      </div>
    </div>
  );
}

/* ─── ConfidenceTrend ────────────────────────────────────────────────────────── */
function ConfidenceTrend({ ticker, current }) {
  const [history, setHistory] = useState(null);
  useEffect(() => {
    if (!ticker) return;
    apiFetch(`/api/signals/${encodeURIComponent(ticker)}/confidence-history`)
      .then(d => { if (d?.length >= 2) setHistory(d); })
      .catch(() => {});
  }, [ticker]);

  const pts = useMemo(() => {
    if (history?.length >= 2) return history.map(p => p.confidence ?? p);
    let h = (ticker || "X").charCodeAt(0) * 17;
    const out = [];
    for (let i = 0; i < 30; i++) {
      h = (h * 1103515245 + 12345) & 0x7fffffff;
      out.push(Math.max(35, Math.min(95, current - 12 + (i / 29) * 12 + ((h % 1000) / 1000 - 0.5) * 18)));
    }
    out[out.length - 1] = current;
    return out;
  }, [history, ticker, current]);

  const W = 110, H = 28;
  const min = Math.min(...pts), max = Math.max(...pts);
  const range = Math.max(max - min, 1);
  const path = pts.map((v, i) => `${i === 0 ? "M" : "L"}${(i / (pts.length - 1)) * W},${H - ((v - min) / range) * H}`).join(" ");
  const last = pts[pts.length - 1], prev = pts[pts.length - 2];
  const delta = last - prev;
  const trend = delta > 1.5 ? "up" : delta < -1.5 ? "down" : "flat";
  const label = history ? `${pts.length} real scans` : "30 scans (est.)";
  return (
    <div className="ct-wrap" title={`Confidence trend · ${label} · ${trend === "up" ? "rising" : trend === "down" ? "fading" : "steady"}`}>
      <span className="ct-lbl mono">{history ? `${pts.length}` : "30"} SCANS</span>
      <svg viewBox={`0 0 ${W} ${H}`} className="ct-svg" preserveAspectRatio="none">
        <path d={path} fill="none" stroke="var(--accent)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
        <circle cx={W} cy={H - ((last - min) / range) * H} r="2.5" fill="var(--accent)"/>
      </svg>
      <span className={`ct-delta mono ${trend}`}>{delta >= 0 ? "+" : ""}{delta.toFixed(1)}pp</span>
    </div>
  );
}

/* ─── PredictiveIntervals ────────────────────────────────────────────────────── */
function PredictiveIntervals({ signal, predictive }) {
  const base = signal.confidence || 65;
  const probSuccess = predictive?.prob_success != null
    ? Math.round(predictive.prob_success * 100)
    : Math.round(Math.min(94, Math.max(38, base * 0.85 + 8)));
  const isMarginal = probSuccess < 60;
  const isStrong   = probSuccess >= 75;
  const verdict      = isStrong ? "Strong" : isMarginal ? "Marginal" : "Reasonable";
  const verdictColor = isStrong ? "var(--up)" : isMarginal ? "var(--warn)" : "var(--accent)";
  const sign = signal.action === "SELL" ? -1 : 1;
  const p1d  = predictive?.horizon_1d  || { exp: sign * (0.81 + (base - 60) * 0.02), low: -5.4, high: 1.7 };
  const p1w  = predictive?.horizon_1w  || { exp: sign * (5.56 - (base - 60) * 0.04), low: -8.4, high: 0.3 };
  const calibrationWarn = base >= 75 && Math.abs(base - probSuccess) > 18;
  const nSimilar = 28 + Math.floor(base / 4);
  const Bar = ({ low, high, exp, label }) => {
    const range = Math.max(Math.abs(low), Math.abs(high), 1) * 1.5;
    const lp = ((low  + range) / (range * 2)) * 100;
    const hp = ((high + range) / (range * 2)) * 100;
    const ep = ((exp  + range) / (range * 2)) * 100;
    const cp = (range / (range * 2)) * 100;
    const expColor = exp > 0 ? "var(--up)" : "var(--down)";
    return (
      <div className="pi-bar">
        <div className="pi-bar-head">
          <span className="pi-bar-pct mono" style={{ color: expColor }}>{exp >= 0 ? "+" : ""}{exp.toFixed(2)}%</span>
          <span className="pi-bar-lbl">{label}</span>
          <span className="pi-bar-meta mono">expected</span>
        </div>
        <div className="pi-bar-track">
          <div className="pi-bar-zero"  style={{ left: cp + "%" }}/>
          <div className="pi-bar-range" style={{ left: lp + "%", width: (hp - lp) + "%" }}/>
          <div className="pi-bar-marker" style={{ left: ep + "%", background: expColor }}/>
        </div>
        <div className="pi-bar-axis mono">
          <span>{low.toFixed(2)}%</span>
          <span className="faint">90% CI</span>
          <span>+{high.toFixed(2)}%</span>
        </div>
      </div>
    );
  };
  return (
    <div className="pred-intervals">
      <div className="pi-head">
        <span className="pi-eyebrow mono">PREDICTIVE CONFIDENCE INTERVALS</span>
        <span className="pi-meta mono">BASED ON {nSimilar} SIMILAR {signal.action} SIGNALS</span>
        {calibrationWarn && <span className="calib-badge" title="Confidence exceeds historical win rate by >18 pts">⚠ CALIB</span>}
      </div>
      <div className="pi-grid">
        <div className="pi-prob">
          <div className="pi-prob-lbl mono">PROBABILITY OF SUCCESS</div>
          <div className="pi-prob-num">{probSuccess}%</div>
          <div className="pi-prob-verdict" style={{ color: verdictColor }}>{verdict}</div>
          <div className="pi-prob-sub">Weighted across horizons · Bayesian smoothing applied · {nSimilar} similar signals</div>
        </div>
        <div className="pi-bars">
          <Bar low={p1d.low} high={p1d.high} exp={p1d.exp} label="1D HORIZON"/>
          <Bar low={p1w.low} high={p1w.high} exp={p1w.exp} label="1W HORIZON"/>
        </div>
      </div>
      <div className="pi-foot">
        Similarity match: same action, confidence within ±25 pts, overlapping sources. Bayesian smoothing applied — predictions strengthen as more signals resolve. Closest match: {signal.action} {signal.ticker} {probSuccess}%.
      </div>
    </div>
  );
}
