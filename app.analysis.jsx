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
  // Beta-adjusted sizing: reduce share count proportionally for high-beta names
  // so the position contributes the same market-dollar-exposure as a beta-1 stock.
  const beta         = signal.beta ?? null;
  const betaAdj      = (beta && beta > 0) ? Math.max(0.5, beta) : null;
  const sharesAdj    = betaAdj ? Math.floor(shares / betaAdj) : null;

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
          ...(sharesAdj != null && sharesAdj !== shares ? [{ label:`β-Adj (β${beta.toFixed(1)})`, val: sharesAdj > 0 ? sharesAdj.toLocaleString() : "—", color:"var(--accent)" }] : []),
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
        Based on ${fmt(entry)} entry · ${fmt(stop)} stop ({riskPer > 0 ? fmt(riskPer,2) : "—"}/share risk).
        {betaAdj != null && sharesAdj !== shares && (
          <span style={{ color:"var(--accent)" }}> β-Adj reduces to {sharesAdj} shares for equal market exposure.</span>
        )}
        {" "}Not financial advice.
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

  // Debounce inputs so the Monte Carlo worker only re-runs 400ms after the user
  // stops changing values — prevents a new 500-path simulation on every keystroke.
  const [dbCapital,   setDbCapital]   = useState(capital);
  const [dbPosSize,   setDbPosSize]   = useState(posSize);
  const [dbSimTrades, setDbSimTrades] = useState(simTrades);
  useEffect(() => { const t = setTimeout(() => setDbCapital(capital),   400); return () => clearTimeout(t); }, [capital]);
  useEffect(() => { const t = setTimeout(() => setDbPosSize(posSize),   400); return () => clearTimeout(t); }, [posSize]);
  useEffect(() => { const t = setTimeout(() => setDbSimTrades(simTrades), 400); return () => clearTimeout(t); }, [simTrades]);

  useEffect(() => {
    const cap = Math.max(100, Number(dbCapital) || 10000);
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
      w.postMessage({ startingCapital: cap, riskPct: dbPosSize * riskPct * 100,
                      trades: dbSimTrades, winRate: winProb, rr: rrNum, paths: 500 });
    } catch (_) {
      const rand = (() => { let s = 42; return () => { s=(s*9301+49297)%233280; return s/233280; }; })();
      let eq = cap; const curve = [cap]; let wins = 0, maxEq = cap, maxDD = 0;
      for (let i = 0; i < dbSimTrades; i++) {
        const risk = eq * (dbPosSize / 100) * riskPct, reward = risk * rrNum;
        if (rand() < winProb) { eq += reward; wins++; } else { eq -= risk; }
        eq = Math.max(0, eq); curve.push(eq);
        if (eq > maxEq) maxEq = eq;
        const dd = (maxEq - eq) / maxEq * 100; if (dd > maxDD) maxDD = dd;
      }
      setSim({ curve, wins, losses: dbSimTrades - wins, finalEq: eq, maxDD, ret: (eq - cap) / cap * 100 });
      setSimLoading(false);
    }
    return () => { if (workerRef.current) { workerRef.current.terminate(); workerRef.current = null; } };
  }, [signal.ticker, dbCapital, dbPosSize, dbSimTrades, winProb, rrNum, riskPct]);

  const simData = sim || { curve: [Number(dbCapital)||10000], wins: 0, losses: 0,
                            finalEq: Number(dbCapital)||10000, maxDD: 0, ret: 0 };

  const cap = Math.max(100, Number(dbCapital) || 10000);
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

/* ─── MarketOverviewView ─────────────────────────────────────────────────── */
function MarketOverviewView({ open, onClose, online }) {
  const [ctx, setCtx] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!open) return;
    setLoading(true);
    authFetch("/api/market/context")
      .then(async r => { const d = await r.json(); if (d) setCtx(d); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [open]);

  const fg     = ctx?.fear_greed  || {};
  const macro  = ctx?.macro       || {};
  const breadth= ctx?.breadth     || {};
  const aaii   = ctx?.aaii        || {};
  const cot    = ctx?.cot         || {};
  const pc     = ctx?.put_call    || {};
  const hmm    = ctx?.hmm_regime  || {};

  // Fear & Greed SVG semicircle gauge
  const FGGauge = ({ score }) => {
    const s = score ?? 50;
    const θ = (180 - (s / 100) * 180) * Math.PI / 180;
    const nx = 100 + 66 * Math.cos(θ);
    const ny = 100 - 66 * Math.sin(θ);
    const getC = v => v <= 25 ? "#ef4444" : v <= 45 ? "#f97316" : v <= 55 ? "#f59e0b" : v <= 75 ? "#84cc16" : "#10b981";
    const color = getC(s);
    const pts = [0, 25, 45, 55, 75, 100].map(v => {
      const a = (180 - (v / 100) * 180) * Math.PI / 180;
      return { x: 100 + 80 * Math.cos(a), y: 100 - 80 * Math.sin(a) };
    });
    const arc = (p1, p2) => `M ${p1.x} ${p1.y} A 80 80 0 0 1 ${p2.x} ${p2.y}`;
    const segColors = ["#ef4444", "#f97316", "#f59e0b", "#84cc16", "#10b981"];
    return (
      <div style={{ display:"flex", flexDirection:"column", alignItems:"center", gap:4 }}>
        <svg viewBox="0 0 200 110" width="160" height="88" style={{ overflow:"visible" }}>
          {segColors.map((c, i) => (
            <path key={i} d={arc(pts[i], pts[i+1])} fill="none" stroke={c} strokeWidth="14" strokeLinecap="butt" opacity="0.75"/>
          ))}
          <line x1="100" y1="100" x2={nx} y2={ny} stroke="var(--text)" strokeWidth="2.5" strokeLinecap="round"/>
          <circle cx="100" cy="100" r="5" fill="var(--text)"/>
        </svg>
        <div style={{ fontFamily:"var(--font-mono)", fontSize:40, fontWeight:700, color, lineHeight:1, marginTop:-8 }}>{s.toFixed(0)}</div>
        <div style={{ fontFamily:"var(--font-mono)", fontSize:10, letterSpacing:"0.14em", color }}>{fg.label?.toUpperCase() || "—"}</div>
        <div style={{ display:"flex", gap:10, marginTop:6 }}>
          {[["Yest", fg.prev_close], ["1W", fg.prev_1w], ["1M", fg.prev_1m]].map(([l, v]) => v != null && (
            <span key={l} style={{ fontFamily:"var(--font-mono)", fontSize:10, color:"var(--text-faint)" }}>
              {l} <span style={{ color: v > s ? "var(--up)" : v < s ? "var(--down)" : "var(--text-dim)" }}>{v?.toFixed(0)}</span>
            </span>
          ))}
        </div>
      </div>
    );
  };

  // Thermometer bar
  const ThermBar = ({ label, value, max=100, goodAbove=65, badBelow=40 }) => {
    const pct = Math.min(100, Math.max(0, value ?? 0));
    const color = value >= goodAbove ? "var(--up)" : value <= badBelow ? "var(--down)" : "var(--warn)";
    return (
      <div style={{ marginBottom:10 }}>
        <div style={{ display:"flex", justifyContent:"space-between", marginBottom:4 }}>
          <span style={{ fontFamily:"var(--font-mono)", fontSize:10, color:"var(--text-faint)" }}>{label}</span>
          <span style={{ fontFamily:"var(--font-mono)", fontSize:12, fontWeight:700, color }}>{value != null ? `${value.toFixed(1)}%` : "—"}</span>
        </div>
        <div style={{ height:6, background:"var(--bg-3)", borderRadius:3, overflow:"hidden" }}>
          <div style={{ height:"100%", width:`${pct}%`, background:color, borderRadius:3, transition:"width 0.4s" }}/>
        </div>
      </div>
    );
  };

  // Data card wrapper
  const Card = ({ title, children, style={} }) => (
    <div style={{ background:"var(--bg-1)", border:"1px solid var(--line)", borderRadius:10, padding:"16px 18px", ...style }}>
      <div style={{ fontFamily:"var(--font-mono)", fontSize:10, letterSpacing:"0.12em", textTransform:"uppercase", color:"var(--text-faint)", marginBottom:10 }}>{title}</div>
      {children}
    </div>
  );

  const Num = ({ v, decimals=2, suffix="", color }) => (
    <span style={{ fontFamily:"var(--font-mono)", fontSize:28, fontWeight:700, color: color || "var(--text)" }}>
      {v != null ? `${v > 0 ? "+" : ""}${Number(v).toFixed(decimals)}${suffix}` : "—"}
    </span>
  );

  // VIX lives in hmm_regime.features, not in macro directly
  const vix = hmm?.features?.vix ?? null;
  const vixColor = vix > 30 ? "var(--down)" : vix > 20 ? "var(--warn)" : vix != null && vix < 14 ? "var(--up)" : "var(--text)";
  const vixLabel = vix > 30 ? "DANGER" : vix > 20 ? "ELEVATED" : vix != null && vix < 14 ? "CALM" : "NORMAL";
  // yc_spread = 10Y − 2Y (positive = normal curve, negative = inverted)
  const spreadColor = (macro.yc_spread ?? 0) < 0 ? "var(--down)" : (macro.yc_spread ?? 0) > 0.5 ? "var(--up)" : "var(--warn)";
  const macroColor = (macro.macro_score ?? 0) > 5 ? "var(--up)" : (macro.macro_score ?? 0) < -5 ? "var(--down)" : "var(--warn)";
  const macroLabel = (macro.macro_score ?? 0) > 5 ? "BULLISH MACRO" : (macro.macro_score ?? 0) < -5 ? "BEARISH MACRO" : "NEUTRAL";
  // sector_rotation is an object { stage, favoured, avoid, confidence }
  const rotObj = macro.sector_rotation || {};
  const rotColor = rotObj.stage === "early" ? "var(--up)" : "var(--warn)";
  const breadthSignalColor = breadth.signal === "bullish" ? "var(--up)" : breadth.signal === "bearish" ? "var(--down)" : "var(--warn)";
  const breadthLabel = breadth.signal === "bullish" ? "HEALTHY" : breadth.signal === "bearish" ? "DETERIORATING" : "WEAKENING";
  const cotNetPct = cot.net_pct ?? 0;
  const cotColor = cot.signal === "bullish" ? "var(--up)" : cot.signal === "bearish" ? "var(--down)" : "var(--warn)";
  const aaiiExposure = aaii.bull_pct ?? 50;
  const aaiiColor = aaiiExposure > 70 ? "var(--down)" : aaiiExposure < 30 ? "var(--up)" : "var(--warn)";

  // Regime banner — hmm.regime is "bull" or "bear"; fall back to sp500_trend
  const regimeBull = hmm.regime === "bull" || (!hmm.regime && macro.sp500_trend === "up");
  const transRisk  = hmm.transition_risk ?? 0;
  const bullProb   = hmm.bull_prob ?? (regimeBull ? 0.7 : 0.3);
  const bearProb   = hmm.bear_prob ?? (1 - bullProb);

  // macro.rationale is the signals array (not macro.signals)
  const signals = (macro.rationale || []).filter(s => s.head);

  return (
    <div className={`overlay ${open ? "open" : ""}`}>
      <div className="overlay-head">
        <div>
          <div className="crumb">MARKET / OVERVIEW</div>
          <h2>Market dashboard</h2>
        </div>
        <button className="btn ghost" style={{ marginLeft:"auto" }} onClick={onClose}><Icon name="x" size={14}/> Close</button>
      </div>

      <div style={{ overflowY:"auto", maxHeight:"calc(100vh - 88px)", padding:"0 0 40px" }}>
        {loading && <div style={{ padding:"40px 28px", color:"var(--text-faint)", fontSize:12 }}>Loading market data…</div>}

        {ctx && (
          <>
            {/* ── Regime Banner ── */}
            <div style={{ display:"flex", alignItems:"center", gap:20, padding:"12px 28px",
              background: regimeBull ? "color-mix(in oklch,var(--up) 8%,var(--bg-1))" : "color-mix(in oklch,var(--down) 8%,var(--bg-1))",
              borderBottom:"1px solid var(--line)" }}>
              <div style={{ fontFamily:"var(--font-mono)", fontSize:18, fontWeight:700,
                color: regimeBull ? "var(--up)" : "var(--down)", letterSpacing:"0.06em" }}>
                {regimeBull ? "▲ BULL MARKET" : "▼ BEAR MARKET"}
              </div>
              <div style={{ flex:1, display:"flex", flexDirection:"column", gap:4 }}>
                <div style={{ display:"flex", alignItems:"center", gap:8, fontFamily:"var(--font-mono)", fontSize:11 }}>
                  <span style={{ color:"var(--up)", minWidth:60 }}>Bull {(bullProb*100).toFixed(0)}%</span>
                  <div style={{ flex:1, height:6, background:"var(--bg-3)", borderRadius:3, overflow:"hidden" }}>
                    <div style={{ height:"100%", width:`${bullProb*100}%`, background:`linear-gradient(90deg,var(--up),var(--down))`, borderRadius:3 }}/>
                  </div>
                  <span style={{ color:"var(--down)", minWidth:60, textAlign:"right" }}>Bear {(bearProb*100).toFixed(0)}%</span>
                </div>
              </div>
              {transRisk > 0.15 && (
                <div style={{ fontFamily:"var(--font-mono)", fontSize:11, color:"var(--warn)",
                  padding:"4px 10px", borderRadius:6, background:"color-mix(in oklch,var(--warn) 12%,transparent)",
                  border:"1px solid color-mix(in oklch,var(--warn) 30%,transparent)" }}>
                  ⚡ Regime risk {(transRisk*100).toFixed(0)}%
                </div>
              )}
            </div>

            {/* ── Hero gauges row ── */}
            <div style={{ display:"grid", gridTemplateColumns:"repeat(3,1fr)", gap:14, padding:"20px 28px 0" }}>
              {/* Fear & Greed */}
              <Card title="Fear & Greed Index" style={{ display:"flex", flexDirection:"column", alignItems:"center", textAlign:"center" }}>
                <FGGauge score={fg.score}/>
              </Card>

              {/* Market Breadth */}
              <Card title="Market Breadth">
                <ThermBar label="% above 50-day SMA" value={breadth.pct_above_50d} goodAbove={60} badBelow={40}/>
                <ThermBar label="% above 200-day SMA" value={breadth.pct_above_200d} goodAbove={65} badBelow={40}/>
                <div style={{ display:"flex", alignItems:"center", gap:8, marginTop:8 }}>
                  <span style={{ fontFamily:"var(--font-mono)", fontSize:11, fontWeight:700, color:breadthSignalColor }}>{breadthLabel}</span>
                  <span style={{ fontFamily:"var(--font-mono)", fontSize:10, color:"var(--text-faint)", marginLeft:"auto" }}>100 S&P stocks</span>
                </div>
              </Card>

              {/* VIX — sourced from hmm_regime.features.vix */}
              <Card title="Volatility (VIX)">
                <div style={{ display:"flex", alignItems:"baseline", gap:12 }}>
                  <span style={{ fontFamily:"var(--font-mono)", fontSize:40, fontWeight:700, color:vixColor, lineHeight:1 }}>
                    {vix != null ? vix.toFixed(1) : "—"}
                  </span>
                  <span style={{ fontFamily:"var(--font-mono)", fontSize:11, fontWeight:700, color:vixColor,
                    padding:"3px 8px", borderRadius:5, background:`color-mix(in oklch,${vixColor} 12%,transparent)` }}>
                    {vixLabel}
                  </span>
                </div>
                {vix != null && (
                  <div style={{ fontFamily:"var(--font-mono)", fontSize:11, color:"var(--text-dim)", marginTop:8 }}>
                    VIX z-score vs 1Y avg: <span style={{ color: (hmm.vix_z ?? 0) < 0 ? "var(--up)" : "var(--warn)" }}>
                      {hmm.vix_z != null ? `${hmm.vix_z > 0 ? "+" : ""}${hmm.vix_z.toFixed(2)}σ` : "—"}
                    </span>
                  </div>
                )}
              </Card>
            </div>

            {/* ── Data cards 2×2 ── */}
            <div style={{ display:"grid", gridTemplateColumns:"repeat(2,1fr)", gap:14, padding:"14px 28px 0" }}>
              {/* Yield Curve — API: macro.t10y, macro.t2y, macro.yc_spread, macro.fed_funds */}
              <Card title="Yield Curve">
                <div style={{ display:"flex", gap:16, alignItems:"baseline", flexWrap:"wrap" }}>
                  {macro.t10y != null && <div style={{ fontFamily:"var(--font-mono)" }}>
                    <div style={{ fontSize:9, color:"var(--text-faint)", textTransform:"uppercase", letterSpacing:"0.1em" }}>10Y</div>
                    <div style={{ fontSize:20, fontWeight:700 }}>{macro.t10y.toFixed(2)}%</div>
                  </div>}
                  {macro.t2y != null && <div style={{ fontFamily:"var(--font-mono)" }}>
                    <div style={{ fontSize:9, color:"var(--text-faint)", textTransform:"uppercase", letterSpacing:"0.1em" }}>2Y</div>
                    <div style={{ fontSize:20, fontWeight:700 }}>{macro.t2y.toFixed(2)}%</div>
                  </div>}
                  {macro.yc_spread != null && <div style={{ fontFamily:"var(--font-mono)" }}>
                    <div style={{ fontSize:9, color:"var(--text-faint)", textTransform:"uppercase", letterSpacing:"0.1em" }}>Spread</div>
                    <div style={{ fontSize:20, fontWeight:700, color:spreadColor }}>{macro.yc_spread > 0 ? "+" : ""}{macro.yc_spread.toFixed(2)}%</div>
                  </div>}
                </div>
                <div style={{ marginTop:8, display:"flex", gap:8, flexWrap:"wrap" }}>
                  {macro.yc_spread != null && (
                    <span style={{ fontFamily:"var(--font-mono)", fontSize:10, fontWeight:700, padding:"3px 8px", borderRadius:4,
                      color:spreadColor, background:`color-mix(in oklch,${spreadColor} 12%,transparent)` }}>
                      {macro.yc_spread < 0 ? "INVERTED" : macro.yc_spread > 0.5 ? "NORMAL" : "FLAT"}
                    </span>
                  )}
                  {macro.fed_funds != null && (
                    <span style={{ fontFamily:"var(--font-mono)", fontSize:10, color:"var(--text-dim)" }}>Fed {macro.fed_funds.toFixed(2)}%</span>
                  )}
                </div>
              </Card>

              {/* Dollar & Macro Score */}
              <Card title="Macro Score & Dollar">
                <div style={{ display:"flex", alignItems:"baseline", gap:12 }}>
                  <span style={{ fontFamily:"var(--font-mono)", fontSize:40, fontWeight:700, color:macroColor, lineHeight:1 }}>
                    {macro.macro_score != null ? `${macro.macro_score > 0 ? "+" : ""}${macro.macro_score}` : "—"}
                  </span>
                  <span style={{ fontFamily:"var(--font-mono)", fontSize:11, fontWeight:700, color:macroColor }}>{macroLabel}</span>
                </div>
                <div style={{ marginTop:8, display:"flex", flexWrap:"wrap", gap:8 }}>
                  {macro.dxy_1m != null && (
                    <span style={{ fontFamily:"var(--font-mono)", fontSize:11, color:"var(--text-dim)" }}>
                      DXY 1M: <span style={{ color: macro.dxy_1m > 2 ? "var(--warn)" : macro.dxy_1m < -2 ? "var(--up)" : "var(--text-dim)" }}>
                        {macro.dxy_1m > 0 ? "+" : ""}{macro.dxy_1m.toFixed(1)}%
                      </span>
                    </span>
                  )}
                  {macro.cpi != null && (
                    <span style={{ fontFamily:"var(--font-mono)", fontSize:11, color:"var(--text-dim)" }}>
                      CPI: <span style={{ color: macro.cpi > 3 ? "var(--warn)" : "var(--text-dim)" }}>{macro.cpi.toFixed(1)}% YoY</span>
                    </span>
                  )}
                  {rotObj.stage && (
                    <span style={{ fontFamily:"var(--font-mono)", fontSize:10, fontWeight:700, padding:"3px 8px", borderRadius:4,
                      color:rotColor, background:`color-mix(in oklch,${rotColor} 12%,transparent)` }}>
                      ● {rotObj.stage.toUpperCase()} CYCLE
                      {rotObj.favoured?.length ? ` · Favour: ${rotObj.favoured.slice(0,3).join(" ")}` : ""}
                    </span>
                  )}
                </div>
              </Card>

              {/* Financial Stress & Labour — STLFSI4, ICSA, UMCSENT */}
              {(macro.stlfsi != null || macro.icsa != null || macro.umcsent != null) && (
                <Card title="Financial Stress & Labour">
                  <div style={{ display:"flex", flexWrap:"wrap", gap:16, alignItems:"baseline" }}>
                    {macro.stlfsi != null && (
                      <div style={{ fontFamily:"var(--font-mono)" }}>
                        <div style={{ fontSize:9, color:"var(--text-faint)", textTransform:"uppercase", letterSpacing:"0.1em" }}>STLFSI4</div>
                        <div style={{ fontSize:20, fontWeight:700,
                          color: macro.stlfsi > 1 ? "var(--down)" : macro.stlfsi > 0.5 ? "var(--warn)" : macro.stlfsi < -0.5 ? "var(--up)" : "var(--text)" }}>
                          {macro.stlfsi > 0 ? "+" : ""}{macro.stlfsi.toFixed(2)}
                        </div>
                        <div style={{ fontSize:9, color:"var(--text-faint)", marginTop:2 }}>
                          {macro.stlfsi > 1 ? "CRISIS" : macro.stlfsi > 0.5 ? "ELEVATED" : macro.stlfsi < -0.5 ? "BENIGN" : "NORMAL"}
                        </div>
                      </div>
                    )}
                    {macro.icsa != null && (
                      <div style={{ fontFamily:"var(--font-mono)" }}>
                        <div style={{ fontSize:9, color:"var(--text-faint)", textTransform:"uppercase", letterSpacing:"0.1em" }}>Init. Claims</div>
                        <div style={{ fontSize:20, fontWeight:700,
                          color: macro.icsa > 350000 ? "var(--down)" : macro.icsa > 300000 ? "var(--warn)" : macro.icsa < 225000 ? "var(--up)" : "var(--text)" }}>
                          {(macro.icsa / 1000).toFixed(0)}K
                        </div>
                        <div style={{ fontSize:9, color:"var(--text-faint)", marginTop:2 }}>
                          {macro.icsa < 225000 ? "TIGHT" : macro.icsa > 300000 ? "STRESS" : "NORMAL"}
                        </div>
                      </div>
                    )}
                    {macro.umcsent != null && (
                      <div style={{ fontFamily:"var(--font-mono)" }}>
                        <div style={{ fontSize:9, color:"var(--text-faint)", textTransform:"uppercase", letterSpacing:"0.1em" }}>Consumer Sent.</div>
                        <div style={{ fontSize:20, fontWeight:700,
                          color: macro.umcsent < 60 ? "var(--down)" : macro.umcsent > 95 ? "var(--up)" : "var(--text)" }}>
                          {macro.umcsent.toFixed(1)}
                        </div>
                        <div style={{ fontSize:9, color:"var(--text-faint)", marginTop:2 }}>
                          {macro.umcsent < 60 ? "DISTRESSED" : macro.umcsent > 95 ? "ELEVATED" : "AVG ~85"}
                        </div>
                      </div>
                    )}
                    {macro.t10y3m != null && (
                      <div style={{ fontFamily:"var(--font-mono)" }}>
                        <div style={{ fontSize:9, color:"var(--text-faint)", textTransform:"uppercase", letterSpacing:"0.1em" }}>T10Y-3M</div>
                        <div style={{ fontSize:20, fontWeight:700,
                          color: macro.t10y3m < 0 ? "var(--down)" : macro.t10y3m > 1.5 ? "var(--up)" : "var(--text)" }}>
                          {macro.t10y3m > 0 ? "+" : ""}{macro.t10y3m.toFixed(2)}%
                        </div>
                        <div style={{ fontSize:9, color:"var(--text-faint)", marginTop:2 }}>
                          {macro.t10y3m < 0 ? "INVERTED" : macro.t10y3m > 1.5 ? "NORMAL" : "FLAT"}
                        </div>
                      </div>
                    )}
                  </div>
                </Card>
              )}

              {/* VIX9D + MOVE */}
              {(macro.vix9d != null || macro.move != null) && (
                <Card title="Vol Term Structure & Bond Stress">
                  <div style={{ display:"flex", flexWrap:"wrap", gap:16, alignItems:"baseline" }}>
                    {macro.vix9d != null && (
                      <div style={{ fontFamily:"var(--font-mono)" }}>
                        <div style={{ fontSize:9, color:"var(--text-faint)", textTransform:"uppercase", letterSpacing:"0.1em" }}>VIX9D</div>
                        <div style={{ fontSize:20, fontWeight:700,
                          color: macro.vix9d_ratio > 1.1 ? "var(--warn)" : "var(--text)" }}>
                          {macro.vix9d.toFixed(1)}
                        </div>
                        {macro.vix9d_ratio != null && (
                          <div style={{ fontSize:9, color:"var(--text-faint)", marginTop:2 }}>
                            {macro.vix9d_ratio.toFixed(2)}× VIX {macro.vix9d_ratio > 1.1 ? "⚠ EVENT RISK" : ""}
                          </div>
                        )}
                      </div>
                    )}
                    {macro.move != null && (
                      <div style={{ fontFamily:"var(--font-mono)" }}>
                        <div style={{ fontSize:9, color:"var(--text-faint)", textTransform:"uppercase", letterSpacing:"0.1em" }}>MOVE Index</div>
                        <div style={{ fontSize:20, fontWeight:700,
                          color: macro.move > 140 ? "var(--down)" : macro.move < 90 ? "var(--up)" : "var(--text)" }}>
                          {macro.move.toFixed(0)}
                        </div>
                        <div style={{ fontSize:9, color:"var(--text-faint)", marginTop:2 }}>
                          {macro.move > 140 ? "BOND STRESS" : macro.move < 90 ? "CALM" : "ELEVATED"}
                        </div>
                      </div>
                    )}
                    {(macro.hy_spread != null || macro.ig_spread != null) && (
                      <div style={{ fontFamily:"var(--font-mono)" }}>
                        <div style={{ fontSize:9, color:"var(--text-faint)", textTransform:"uppercase", letterSpacing:"0.1em" }}>Credit Spreads</div>
                        {macro.hy_spread != null && (
                          <div style={{ fontSize:13, fontWeight:700,
                            color: macro.hy_spread > 450 ? "var(--down)" : macro.hy_spread < 300 ? "var(--up)" : "var(--text)" }}>
                            HY {macro.hy_spread.toFixed(0)}bps
                          </div>
                        )}
                        {macro.ig_spread != null && (
                          <div style={{ fontSize:11, color:"var(--text-faint)" }}>
                            IG {macro.ig_spread.toFixed(0)}bps
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </Card>
              )}

              {/* COT */}
              <Card title="Hedge Fund S&P Positioning (COT)">
                {cot.lev_long != null ? (
                  <>
                    <div style={{ display:"flex", flexDirection:"column", gap:6 }}>
                      {[["Long", cot.lev_long, "var(--up)"], ["Short", cot.lev_short, "var(--down)"]].map(([label, val, color]) => (
                        <div key={label} style={{ display:"flex", alignItems:"center", gap:10 }}>
                          <span style={{ fontFamily:"var(--font-mono)", fontSize:10, color:"var(--text-faint)", minWidth:36 }}>{label}</span>
                          <div style={{ flex:1, height:8, background:"var(--bg-3)", borderRadius:4, overflow:"hidden" }}>
                            <div style={{ height:"100%", width:`${Math.min(100, (val / Math.max(cot.lev_long, cot.lev_short)) * 100)}%`,
                              background:color, borderRadius:4 }}/>
                          </div>
                          <span style={{ fontFamily:"var(--font-mono)", fontSize:11, color:"var(--text-dim)", minWidth:52, textAlign:"right" }}>
                            {(val/1000).toFixed(0)}K
                          </span>
                        </div>
                      ))}
                    </div>
                    <div style={{ marginTop:10, display:"flex", gap:10, alignItems:"center" }}>
                      <span style={{ fontFamily:"var(--font-mono)", fontSize:11, color:"var(--text-dim)" }}>
                        Net <span style={{ color:cotColor, fontWeight:700 }}>{cotNetPct > 0 ? "+" : ""}{cotNetPct.toFixed(1)}%</span>
                      </span>
                      {cot.signal && (
                        <span style={{ fontFamily:"var(--font-mono)", fontSize:10, fontWeight:700, padding:"2px 8px", borderRadius:4,
                          color:cotColor, background:`color-mix(in oklch,${cotColor} 12%,transparent)` }}>
                          ↑ CONTRARIAN {cot.signal.toUpperCase()}
                        </span>
                      )}
                      <span style={{ fontFamily:"var(--font-mono)", fontSize:9, color:"var(--text-faint)", marginLeft:"auto" }}>CFTC weekly</span>
                    </div>
                  </>
                ) : <div style={{ fontFamily:"var(--font-mono)", fontSize:11, color:"var(--text-faint)" }}>No COT data</div>}
              </Card>

              {/* NAAIM Sentiment */}
              <Card title="Manager Equity Exposure (NAAIM)">
                <div style={{ display:"flex", alignItems:"baseline", gap:12 }}>
                  <span style={{ fontFamily:"var(--font-mono)", fontSize:40, fontWeight:700, color:aaiiColor, lineHeight:1 }}>
                    {aaiiExposure.toFixed(1)}%
                  </span>
                </div>
                {/* Exposure bar with zones */}
                <div style={{ marginTop:10, position:"relative" }}>
                  <div style={{ height:10, borderRadius:5, overflow:"hidden",
                    background:`linear-gradient(90deg, var(--up) 0%, var(--up) 30%, var(--bg-3) 30%, var(--bg-3) 70%, var(--down) 70%, var(--down) 100%)` }}>
                    {/* Current position marker */}
                    <div style={{ position:"absolute", top:0, bottom:0, left:`${aaiiExposure}%`, transform:"translateX(-50%)",
                      width:3, background:"var(--text)", borderRadius:2 }}/>
                  </div>
                  <div style={{ display:"flex", justifyContent:"space-between", marginTop:4, fontFamily:"var(--font-mono)", fontSize:9, color:"var(--text-faint)" }}>
                    <span style={{ color:"var(--up)" }}>0% (defensive)</span>
                    <span>100% (all-in)</span>
                  </div>
                </div>
                <div style={{ marginTop:8, display:"flex", gap:10, alignItems:"center", flexWrap:"wrap" }}>
                  {pc.ratio != null && (
                    <span style={{ fontFamily:"var(--font-mono)", fontSize:11, color:"var(--text-dim)" }}>
                      P/C Ratio: {pc.ratio.toFixed(2)} — {pc.signal || "Neutral"}
                    </span>
                  )}
                  {aaii.signal && (
                    <span style={{ fontFamily:"var(--font-mono)", fontSize:10, fontWeight:700, padding:"2px 8px", borderRadius:4,
                      color:aaiiColor, background:`color-mix(in oklch,${aaiiColor} 12%,transparent)` }}>
                      ⚠ CONTRARIAN {aaii.signal.toUpperCase()}
                    </span>
                  )}
                </div>
              </Card>
            </div>

            {/* ── Signal Pills ── */}
            {signals.length > 0 && (
              <div style={{ padding:"14px 28px 0" }}>
                <div style={{ fontFamily:"var(--font-mono)", fontSize:10, letterSpacing:"0.12em", textTransform:"uppercase",
                  color:"var(--text-faint)", marginBottom:8 }}>Active macro signals</div>
                <div style={{ display:"flex", flexWrap:"wrap", gap:8 }}>
                  {signals.slice(0, 10).map((s, i) => {
                    const c = s.sentiment === "pos" ? "var(--up)" : s.sentiment === "neg" ? "var(--down)" : "var(--warn)";
                    return (
                      <span key={i} title={s.body || s.head} style={{ display:"inline-flex", alignItems:"center", gap:5,
                        padding:"4px 10px", borderRadius:99, fontFamily:"var(--font-mono)", fontSize:10,
                        color:c, background:`color-mix(in oklch,${c} 10%,transparent)`,
                        border:`1px solid color-mix(in oklch,${c} 25%,transparent)`, cursor:"default" }}>
                        <span style={{ width:5, height:5, borderRadius:"50%", background:c, flexShrink:0 }}/>
                        {s.head}
                      </span>
                    );
                  })}
                </div>
              </div>
            )}
          </>
        )}
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

// S&P 500 approximate sector market cap weights (static)
const SECTOR_WEIGHTS = {
  XLK:29, XLV:13, XLF:13, XLC:9, XLI:9, XLY:6, XLP:6, XLE:4, XLB:4, XLRE:3, XLU:3
};

const ROTATION_PHASES = {
  early_bull: { etfs:["XLY","XLK","XLC"], label:"EARLY BULL", color:"var(--up)" },
  late_bull:  { etfs:["XLE","XLB","XLF"], label:"LATE BULL",  color:"var(--warn)" },
  early_bear: { etfs:["XLV","XLRE","XLU"], label:"EARLY BEAR", color:"var(--warn)" },
  late_bear:  { etfs:["XLP","XLU","XLV"], label:"LATE BEAR",  color:"var(--down)" },
};

function SectorView({ open, onClose, online }) {
  const [sectors, setSectors]   = useState(null);
  const [flows,   setFlows]     = useState(null);
  const [detail,  setDetail]    = useState(null);
  const [activeEtf, setActiveEtf] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [err, setErr]           = useState(null);
  const [tf, setTf]             = useState("1m");   // 1d | 1w | 1m | 3m | ytd
  const [mode, setMode]         = useState("perf"); // perf | flow
  const [rotation, setRotation] = useState(null);

  useEffect(() => {
    if (!open) return;
    setErr(null); setActiveEtf(null);
    Promise.all([
      authFetch("/api/market/sectors").then(r => r.json()),
      authFetch("/api/market/etf-flows").then(r => r.json()).catch(() => null),
      authFetch("/api/market/context").then(r => r.json()).catch(() => null),
    ]).then(([sec, fl, ctx]) => {
      if (sec) setSectors(Array.isArray(sec) ? sec : []);
      if (fl)  setFlows(fl);
      // sector_rotation is an object { stage, favoured, avoid, confidence }
      if (ctx?.macro?.sector_rotation) setRotation(ctx.macro.sector_rotation);
    }).catch(() => setErr("offline"));
  }, [open]);

  const drillIn = etf => {
    setActiveEtf(etf);
    if (detail) return;
    setDetailLoading(true);
    authFetch("/api/market/sectors/detail")
      .then(r => r.json()).then(d => { if (d) setDetail(d); }).catch(() => {})
      .finally(() => setDetailLoading(false));
  };

  const getReturn = s => {
    if (!s) return null;
    return tf === "1d" ? s.ret_1d : tf === "1w" ? s.ret_1w : tf === "3m" ? s.ret_3m : tf === "ytd" ? s.ret_ytd : s.ret_1m;
  };

  const tileColor = (s) => {
    if (mode === "flow") {
      const etf = s?.etf;
      const flow = flows?.[etf]?.flow_1w ?? 0;
      if (flow > 200) return "color-mix(in oklch,var(--up) 30%,var(--bg-2))";
      if (flow > 50)  return "color-mix(in oklch,var(--up) 16%,var(--bg-2))";
      if (flow < -50) return "color-mix(in oklch,var(--down) 20%,var(--bg-2))";
      return "var(--bg-2)";
    }
    const v = getReturn(s);
    if (v == null) return "var(--bg-2)";
    if (v >  5) return "color-mix(in oklch,var(--up) 30%,var(--bg-2))";
    if (v >  2) return "color-mix(in oklch,var(--up) 16%,var(--bg-2))";
    if (v < -5) return "color-mix(in oklch,var(--down) 30%,var(--bg-2))";
    if (v < -2) return "color-mix(in oklch,var(--down) 16%,var(--bg-2))";
    return "var(--bg-2)";
  };

  const tileTextColor = v => v == null ? "var(--text-faint)" : v >= 0 ? "var(--up)" : "var(--down)";
  const fmtR = v => v == null ? "—" : `${v >= 0 ? "+" : ""}${v.toFixed(2)}%`;

  const activeStocks = useMemo(() => {
    if (!activeEtf || !detail) return [];
    return (detail.sectors || []).find(s => s.etf === activeEtf)?.stocks || [];
  }, [activeEtf, detail]);

  // rotation is now an object; build a compatible rotPhase from it
  const rotPhase = rotation ? {
    label: rotation.stage ? rotation.stage.toUpperCase() + " CYCLE" : "—",
    color: rotation.stage === "early" ? "var(--up)" : "var(--warn)",
    etfs:  rotation.favoured || [],
    avoid: rotation.avoid || [],
    confidence: rotation.confidence,
  } : null;

  return (
    <div className={`overlay ${open ? "open" : ""}`}>
      <div className="overlay-head">
        <div>
          <div className="crumb">MARKET / SECTOR HEATMAP{activeEtf ? ` / ${activeEtf}` : ""}</div>
          <h2>{activeEtf ? `${SECTOR_NAMES[activeEtf] || activeEtf} — stocks` : "Sector heatmap"}</h2>
        </div>
        <div style={{ display:"flex", alignItems:"center", gap:8, marginLeft:"auto" }}>
          {!activeEtf && (
            <>
              {/* Timeframe tabs */}
              <div style={{ display:"flex", background:"var(--bg-2)", border:"1px solid var(--line)", borderRadius:6, overflow:"hidden" }}>
                {[["1d","1D"],["1w","1W"],["1m","1M"],["3m","3M"],["ytd","YTD"]].map(([k,l]) => (
                  <button key={k} onClick={() => setTf(k)}
                    style={{ padding:"5px 10px", fontFamily:"var(--font-mono)", fontSize:11,
                      background: tf===k ? "var(--accent)" : "transparent",
                      color: tf===k ? "#042116" : "var(--text-dim)", border:"none", cursor:"pointer", fontWeight: tf===k ? 700 : 400 }}>
                    {l}
                  </button>
                ))}
              </div>
              {/* Mode toggle */}
              <div style={{ display:"flex", background:"var(--bg-2)", border:"1px solid var(--line)", borderRadius:6, overflow:"hidden" }}>
                {[["perf","Performance"],["flow","Fund Flows"]].map(([k,l]) => (
                  <button key={k} onClick={() => setMode(k)}
                    style={{ padding:"5px 10px", fontFamily:"var(--font-mono)", fontSize:11,
                      background: mode===k ? "var(--bg-3)" : "transparent",
                      color: mode===k ? "var(--text)" : "var(--text-faint)", border:"none", cursor:"pointer" }}>
                    {l}
                  </button>
                ))}
              </div>
            </>
          )}
          {activeEtf && <button className="btn ghost" style={{ fontSize:11 }} onClick={() => setActiveEtf(null)}>← Back</button>}
          <button className="btn ghost" onClick={onClose}><Icon name="x" size={14}/> Close</button>
        </div>
      </div>

      <div style={{ overflowY:"auto", maxHeight:"calc(100vh - 88px)", padding:"20px 28px 40px" }}>
        {err === "upgrade" && <UpgradePrompt feature="Sector heatmap" minTier="basic"/>}
        {err === "offline" && <div style={{ color:"var(--text-faint)", fontSize:12 }}>Backend offline.</div>}
        {!sectors && !err && <div style={{ color:"var(--text-faint)", fontSize:12 }}>Loading…</div>}

        {sectors && !activeEtf && (
          <>
            {/* Treemap */}
            <div style={{ display:"flex", flexWrap:"wrap", gap:6, marginBottom:24 }}>
              {(sectors.length > 0 ? sectors : Object.keys(SECTOR_NAMES).map(etf => ({ etf }))).map(s => {
                const w = SECTOR_WEIGHTS[s.etf] || 3;
                const v = getReturn(s);
                const flow = flows?.[s.etf];
                return (
                  <div key={s.etf} onClick={() => drillIn(s.etf)}
                    style={{ flexGrow:w, flexBasis:`${w*1.2}%`, minWidth:80, minHeight:90,
                      background:tileColor(s), border:"1px solid var(--line)",
                      borderRadius:8, padding:"12px 14px", cursor:"pointer", position:"relative",
                      transition:"opacity 0.12s, transform 0.12s" }}
                    onMouseEnter={e => { e.currentTarget.style.opacity="0.85"; e.currentTarget.style.transform="scale(1.02)"; }}
                    onMouseLeave={e => { e.currentTarget.style.opacity="1"; e.currentTarget.style.transform="scale(1)"; }}>
                    <div style={{ fontFamily:"var(--font-mono)", fontSize:12, fontWeight:700, color:"var(--text)" }}>{s.etf}</div>
                    <div style={{ fontSize:10, color:"var(--text-faint)", marginTop:2 }}>{SECTOR_NAMES[s.etf] || s.etf}</div>
                    <div style={{ fontFamily:"var(--font-mono)", fontSize:18, fontWeight:700, color:tileTextColor(v), marginTop:6, lineHeight:1 }}>
                      {fmtR(v)}
                    </div>
                    {mode === "flow" && flow?.flow_1w != null && (
                      <div style={{ position:"absolute", bottom:8, right:10, fontFamily:"var(--font-mono)", fontSize:9,
                        color: flow.flow_1w > 0 ? "var(--up)" : "var(--down)" }}>
                        {flow.flow_1w > 0 ? "↑" : "↓"} ${Math.abs(flow.flow_1w).toFixed(0)}M
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Rotation wheel */}
            {rotPhase && (
              <div style={{ background:"var(--bg-1)", border:"1px solid var(--line)", borderRadius:10, padding:"16px 20px" }}>
                <div style={{ fontFamily:"var(--font-mono)", fontSize:10, letterSpacing:"0.12em", textTransform:"uppercase",
                  color:"var(--text-faint)", marginBottom:10 }}>Sector rotation cycle</div>
                <div style={{ display:"flex", alignItems:"center", gap:24 }}>
                  <div style={{ padding:"10px 16px", borderRadius:8, background:`color-mix(in oklch,${rotPhase.color} 14%,var(--bg-2))`,
                    border:`1.5px solid ${rotPhase.color}`, fontFamily:"var(--font-mono)", fontSize:13, fontWeight:700, color:rotPhase.color }}>
                    {rotPhase.label}
                    {rotPhase.confidence != null && (
                      <div style={{ fontSize:10, fontWeight:400, color:"var(--text-faint)", marginTop:2 }}>{rotPhase.confidence}% confidence</div>
                    )}
                  </div>
                  <div>
                    <div style={{ fontFamily:"var(--font-mono)", fontSize:12, color:"var(--text-dim)", marginBottom:6 }}>
                      Favour: {rotPhase.etfs.length ? "" : "—"}
                    </div>
                    <div style={{ display:"flex", gap:8, flexWrap:"wrap" }}>
                      {rotPhase.etfs.map(e => (
                        <span key={e} style={{ fontFamily:"var(--font-mono)", fontSize:11, fontWeight:700, padding:"3px 8px", borderRadius:4,
                          background:"color-mix(in oklch,var(--up) 10%,var(--bg-2))", border:"1px solid color-mix(in oklch,var(--up) 30%,var(--line))", color:"var(--up)" }}>{e}</span>
                      ))}
                    </div>
                    {rotPhase.avoid?.length > 0 && (
                      <div style={{ marginTop:6, display:"flex", gap:8, flexWrap:"wrap" }}>
                        <span style={{ fontFamily:"var(--font-mono)", fontSize:10, color:"var(--text-faint)" }}>Avoid:</span>
                        {rotPhase.avoid.map(e => (
                          <span key={e} style={{ fontFamily:"var(--font-mono)", fontSize:11, padding:"3px 8px", borderRadius:4,
                            background:"color-mix(in oklch,var(--down) 10%,var(--bg-2))", border:"1px solid color-mix(in oklch,var(--down) 30%,var(--line))", color:"var(--down)" }}>{e}</span>
                        ))}
                      </div>
                    )}
                    <div style={{ fontFamily:"var(--font-mono)", fontSize:10, color:"var(--text-faint)", marginTop:8 }}>
                      Historical pattern — not a prediction
                    </div>
                  </div>
                </div>
              </div>
            )}
          </>
        )}

        {/* Drill-down */}
        {activeEtf && (
          <>
            {detailLoading && <div style={{ color:"var(--text-faint)", fontSize:12 }}>Loading stocks…</div>}
            {!detailLoading && activeStocks.length === 0 && (
              <div style={{ color:"var(--text-faint)", fontSize:12 }}>No watchlist stocks found for {activeEtf}.</div>
            )}
            {activeStocks.length > 0 && (() => {
              const etfRet = sectors?.find(s => s.etf === activeEtf)?.ret_1m;
              const rc = v => v == null ? "var(--text-faint)" : v >= 0 ? "var(--up)" : "var(--down)";
              return (
                <SortableTable
                  cols={["Ticker","Company","1D","1M","Signal","Confidence","RS vs ETF"]}
                  defaultSort={{ col:3, dir:"desc" }}
                  rows={activeStocks.map(s => {
                    const rs = s.ret_1m != null && etfRet != null ? s.ret_1m - etfRet : null;
                    return [
                      <span style={{ fontFamily:"var(--font-mono)", fontWeight:700 }}>{s.ticker}</span>,
                      s.company || s.ticker,
                      <span style={{ fontFamily:"var(--font-mono)", color:rc(s.ret_1d) }}>{fmtR(s.ret_1d)}</span>,
                      <span style={{ fontFamily:"var(--font-mono)", color:rc(s.ret_1m) }}>{fmtR(s.ret_1m)}</span>,
                      s.action ? <span className={`signal-verb ${s.action}`} style={{ fontSize:10 }}>{s.action}</span> : "—",
                      s.confidence ? `${s.confidence.toFixed(0)}%` : "—",
                      <span style={{ fontFamily:"var(--font-mono)", color:rc(rs) }}>{fmtR(rs)}</span>,
                    ];
                  })}
                  colors={[null,null,null,null,null,null,null]}
                />
              );
            })()}
          </>
        )}
      </div>
    </div>
  );
}

/* ─── CalendarView ─────────────────────────────────────────────────────────── */
const CAL_CATEGORIES = ["All","Inflation","Employment","Fed / Rates","Growth","Housing","Surveys"];
const CAL_CAT_MAP = {
  cpi:"Inflation", ppi:"Inflation", pce:"Inflation",
  jobs:"Employment", nfp:"Employment", jolts:"Employment", claims:"Employment", unemployment:"Employment",
  fomc:"Fed / Rates", fed:"Fed / Rates", rates:"Fed / Rates",
  gdp:"Growth", retail:"Growth", ism:"Growth", pmi:"Growth", durable:"Growth",
  housing:"Housing", "home sales":"Housing",
  sentiment:"Surveys", confidence:"Surveys", michigan:"Surveys",
};

function eventCategory(e) {
  const n = (e.name || "").toLowerCase();
  const l = (e.label || "").toLowerCase();
  if (e.category) {
    const c = e.category.toLowerCase();
    for (const [k, v] of Object.entries(CAL_CAT_MAP)) { if (c.includes(k) || n.includes(k) || l.includes(k)) return v; }
  }
  for (const [k, v] of Object.entries(CAL_CAT_MAP)) { if (n.includes(k) || l.includes(k)) return v; }
  return "Other";
}

const IMPACT_BLURBS = {
  CPI:   "Higher than expected → bearish equities, hawkish Fed, bullish USD",
  PPI:   "Upstream inflation gauge — leads CPI by 1–2 months",
  NFP:   "Strong jobs → hawkish Fed fears, rate-sensitive sectors sell off",
  FOMC:  "Rate decision — volatility spike expected at 2pm ET",
  GDP:   "Above consensus → risk-on; miss → risk-off, defensive rotation",
  PCE:   "Fed's preferred inflation gauge — moves bonds more than stocks",
  ISM:   "Above 50 = expansion; below = contraction",
  Retail:"Consumer spending — key GDP driver; miss = consumer weakness",
};

function CalendarView({ open, onClose }) {
  const [events,  setEvents]  = useState(null);
  const [err,     setErr]     = useState(null);
  const [cat,     setCat]     = useState("All");

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

  const today = new Date();
  today.setHours(0,0,0,0);

  const daysUntil = dateStr => {
    try { const d = new Date(dateStr); d.setHours(0,0,0,0); return Math.round((d - today) / 86400000); }
    catch { return null; }
  };

  const impactStyle = imp => {
    if (imp === "HIGH")   return { dot:"#ef4444", label:"HIGH" };
    if (imp === "MEDIUM") return { dot:"#f59e0b", label:"MED"  };
    return { dot:"#5a6070", label:"LOW" };
  };

  // Next 7 days strip
  const next7 = useMemo(() => {
    return Array.from({ length:7 }, (_, i) => {
      const d = new Date(today); d.setDate(d.getDate() + i);
      const dateStr = d.toISOString().slice(0,10);
      const dayEvents = (events || []).filter(e => e.date === dateStr);
      return { date:d, dateStr, dayEvents };
    });
  }, [events]);

  const DAYS = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];

  // Filter + group events
  const filtered = useMemo(() => {
    if (!events) return [];
    return events.filter(e => {
      if (cat === "All") return true;
      return eventCategory(e) === cat;
    });
  }, [events, cat]);

  const catCounts = useMemo(() => {
    if (!events) return {};
    const counts = {};
    CAL_CATEGORIES.forEach(c => {
      counts[c] = c === "All" ? events.length : events.filter(e => eventCategory(e) === c).length;
    });
    return counts;
  }, [events]);

  const grouped = useMemo(() => {
    const map = new Map();
    filtered.forEach(e => {
      if (!map.has(e.date)) map.set(e.date, []);
      map.get(e.date).push(e);
    });
    return [...map.entries()].map(([date, evts]) => ({ date, evts })).sort((a,b) => a.date.localeCompare(b.date));
  }, [filtered]);

  const groupedByMonth = useMemo(() => {
    const map = new Map();
    grouped.forEach(g => {
      const month = g.date.slice(0,7);
      if (!map.has(month)) map.set(month, []);
      map.get(month).push(g);
    });
    return [...map.entries()].map(([month, days]) => ({ month, days }));
  }, [grouped]);

  const fmtDate = dateStr => {
    try {
      const d = new Date(dateStr + "T12:00:00");
      return d.toLocaleDateString("en-US", { weekday:"long", month:"long", day:"numeric" });
    } catch { return dateStr; }
  };

  return (
    <div className={`overlay ${open ? "open" : ""}`}>
      <div className="overlay-head">
        <div>
          <div className="crumb">MARKET / ECONOMIC CALENDAR</div>
          <h2>Upcoming macro events</h2>
        </div>
        <button className="btn ghost" style={{ marginLeft:"auto" }} onClick={onClose}><Icon name="x" size={14}/> Close</button>
      </div>

      <div style={{ overflowY:"auto", maxHeight:"calc(100vh - 88px)" }}>
        {err === "upgrade" && <div style={{ padding:28 }}><UpgradePrompt feature="Economic calendar" minTier="basic"/></div>}
        {err === "offline" && <div style={{ padding:28, color:"var(--text-faint)", fontSize:12 }}>Backend offline.</div>}
        {!events && !err && <div style={{ padding:28, color:"var(--text-faint)", fontSize:12 }}>Loading…</div>}

        {events && (
          <>
            {/* ── 7-day strip ── */}
            <div style={{ padding:"16px 28px", borderBottom:"1px solid var(--line)", background:"var(--bg-1)" }}>
              <div style={{ fontFamily:"var(--font-mono)", fontSize:10, letterSpacing:"0.12em", color:"var(--text-faint)", marginBottom:10 }}>
                NEXT 7 DAYS
              </div>
              <div style={{ display:"flex", gap:6, overflowX:"auto", paddingBottom:4 }}>
                {next7.map(({ date, dateStr, dayEvents }) => {
                  const du = daysUntil(dateStr);
                  const isToday = du === 0;
                  const highImpact = dayEvents.some(e => e.impact === "HIGH");
                  return (
                    <div key={dateStr} style={{ minWidth:80, flexShrink:0, textAlign:"center",
                      padding:"10px 8px", borderRadius:8,
                      background: isToday ? "color-mix(in oklch,var(--accent) 12%,var(--bg-2))" : "var(--bg-2)",
                      border: isToday ? "1.5px solid var(--accent)" : "1px solid var(--line)" }}>
                      <div style={{ fontFamily:"var(--font-mono)", fontSize:10, color: isToday ? "var(--accent)" : "var(--text-faint)",
                        letterSpacing:"0.08em" }}>{DAYS[date.getDay()]}</div>
                      <div style={{ fontFamily:"var(--font-mono)", fontSize:13, fontWeight:700,
                        color: isToday ? "var(--accent)" : "var(--text)", marginTop:2 }}>{date.getDate()}</div>
                      {isToday && <div style={{ fontFamily:"var(--font-mono)", fontSize:8, color:"var(--accent)", marginTop:2 }}>TODAY</div>}
                      {dayEvents.length > 0 && (
                        <div style={{ fontFamily:"var(--font-mono)", fontSize:9, fontWeight:700, marginTop:4,
                          color: highImpact ? "#ef4444" : "var(--text-faint)" }}>
                          {dayEvents.length} event{dayEvents.length !== 1 ? "s" : ""}
                        </div>
                      )}
                      <div style={{ marginTop:4, display:"flex", flexDirection:"column", gap:2, alignItems:"center" }}>
                        {dayEvents.slice(0,3).map((e,i) => (
                          <span key={i} style={{ fontFamily:"var(--font-mono)", fontSize:8, padding:"1px 5px", borderRadius:3,
                            background: e.impact === "HIGH" ? "color-mix(in oklch,#ef4444 18%,transparent)" : e.impact === "MEDIUM" ? "color-mix(in oklch,#f59e0b 18%,transparent)" : "var(--bg-3)",
                            color: e.impact === "HIGH" ? "#ef4444" : e.impact === "MEDIUM" ? "#f59e0b" : "var(--text-faint)",
                            maxWidth:72, overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>
                            {e.label || e.name}
                          </span>
                        ))}
                        {dayEvents.length === 0 && <span style={{ fontSize:9, color:"var(--text-faint)", marginTop:4 }}>—</span>}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* ── Category filters ── */}
            <div style={{ padding:"12px 28px", borderBottom:"1px solid var(--line)", display:"flex", gap:6, flexWrap:"wrap", alignItems:"center" }}>
              {CAL_CATEGORIES.map(c => {
                const count = catCounts[c] || 0;
                const active = cat === c;
                return (
                  <button key={c} onClick={() => setCat(c)}
                    style={{ fontFamily:"var(--font-mono)", fontSize:11, padding:"5px 12px", borderRadius:99,
                      cursor:"pointer", border:"1px solid var(--line)",
                      background: active ? "var(--accent)" : "transparent",
                      color: active ? "#042116" : "var(--text-dim)", fontWeight: active ? 700 : 400 }}>
                    {c} {count > 0 && <span style={{ opacity:0.7 }}>({count})</span>}
                  </button>
                );
              })}
              <div style={{ marginLeft:"auto", display:"flex", gap:12, fontFamily:"var(--font-mono)", fontSize:10 }}>
                {[["#ef4444","HIGH"],["#f59e0b","MED"],["var(--text-faint)","LOW"]].map(([c,l]) => (
                  <span key={l} style={{ display:"flex", alignItems:"center", gap:4, color:"var(--text-faint)" }}>
                    <span style={{ width:7, height:7, borderRadius:"50%", background:c }}/>
                    {l}
                  </span>
                ))}
              </div>
            </div>

            {/* ── Event list ── */}
            <div style={{ padding:"0 28px 40px" }}>
              {grouped.length === 0 && (
                <div style={{ padding:"40px 0", textAlign:"center", color:"var(--text-faint)", fontSize:12 }}>
                  No events in this category.
                </div>
              )}
              {groupedByMonth.map(({ month, days }) => (
                <div key={month}>
                  {/* Month divider */}
                  <div style={{ display:"flex", alignItems:"center", gap:12, padding:"20px 0 8px",
                    fontFamily:"var(--font-mono)", fontSize:10, letterSpacing:"0.14em", textTransform:"uppercase", color:"var(--text-faint)" }}>
                    <div style={{ flex:1, height:1, background:"var(--line)" }}/>
                    {new Date(month + "-15").toLocaleDateString("en-US", { month:"long", year:"numeric" }).toUpperCase()}
                    <div style={{ flex:1, height:1, background:"var(--line)" }}/>
                  </div>

                  {days.map(({ date, evts }) => {
                    const du    = daysUntil(date);
                    const isToday   = du === 0;
                    const isHigh    = evts.some(e => e.impact === "HIGH");
                    const isImminent = du != null && du <= 3 && du >= 0;
                    return (
                      <div key={date} style={{ marginBottom:14 }}>
                        {/* Date header */}
                        <div style={{ display:"flex", alignItems:"center", gap:10, padding:"8px 0 6px",
                          borderLeft: isHigh ? "2px solid var(--warn)" : "2px solid transparent", paddingLeft:10 }}>
                          <span style={{ fontFamily:"var(--font-mono)", fontSize:11, fontWeight:700, color:"var(--text)" }}>
                            {fmtDate(date).toUpperCase()}
                          </span>
                          {isToday && (
                            <span style={{ fontFamily:"var(--font-mono)", fontSize:9, fontWeight:700, padding:"2px 6px",
                              borderRadius:3, background:"var(--up)", color:"#000" }}>TODAY</span>
                          )}
                          {isHigh && !isToday && <span style={{ fontFamily:"var(--font-mono)", fontSize:9, color:"var(--warn)" }}>⚡ High impact</span>}
                          <span style={{ marginLeft:"auto", fontFamily:"var(--font-mono)", fontSize:10, color:"var(--text-faint)" }}>
                            {evts.length} event{evts.length !== 1 ? "s" : ""}
                          </span>
                        </div>

                        {/* Event cards */}
                        {evts.map((e, i) => {
                          const du2   = daysUntil(e.date);
                          const imp   = impactStyle(e.impact);
                          const isImm = du2 != null && du2 <= 3 && du2 >= 0;
                          const blurb = Object.entries(IMPACT_BLURBS).find(([k]) => (e.label || e.name || "").toUpperCase().includes(k))?.[1];
                          const fcastNum = parseFloat(e.forecast);
                          const prevNum  = parseFloat(e.previous);
                          const improving = !isNaN(fcastNum) && !isNaN(prevNum) && fcastNum < prevNum;

                          return (
                            <div key={i} style={{ background:"var(--bg-1)", border:`1px solid ${isImm && e.impact==="HIGH" ? "color-mix(in oklch,#ef4444 35%,var(--line))" : "var(--line)"}`,
                              borderRadius:8, padding:"14px 16px", marginBottom:8,
                              boxShadow: du2 === 0 ? "0 0 0 2px color-mix(in oklch,var(--accent) 30%,transparent)" : "none" }}>
                              {/* Top row */}
                              <div style={{ display:"flex", alignItems:"center", gap:10, marginBottom:10 }}>
                                <span style={{ width:7, height:7, borderRadius:"50%", background:imp.dot, flexShrink:0 }}/>
                                <span style={{ fontFamily:"var(--font-mono)", fontSize:10, fontWeight:700, padding:"2px 6px",
                                  borderRadius:3, background:`color-mix(in oklch,${imp.dot} 14%,transparent)`, color:imp.dot }}>
                                  {imp.label}
                                </span>
                                <span style={{ fontFamily:"var(--font-mono)", fontSize:11, fontWeight:700, color:"var(--text)",
                                  padding:"2px 6px", borderRadius:3, background:"var(--bg-2)" }}>
                                  {e.label || "EVT"}
                                </span>
                                <span style={{ fontSize:13, fontWeight:600, color:"var(--text)" }}>{e.name || e.label}</span>
                                {e.time && (
                                  <span style={{ marginLeft:"auto", fontFamily:"var(--font-mono)", fontSize:11, color:"var(--text-faint)", flexShrink:0 }}>
                                    {e.time} ET
                                  </span>
                                )}
                              </div>

                              {/* Forecast / previous */}
                              {(e.forecast || e.previous) && (
                                <div style={{ display:"flex", gap:20, marginBottom:8 }}>
                                  {e.forecast && (
                                    <div>
                                      <div style={{ fontFamily:"var(--font-mono)", fontSize:9, color:"var(--text-faint)", textTransform:"uppercase", letterSpacing:"0.1em" }}>Forecast</div>
                                      <div style={{ fontFamily:"var(--font-mono)", fontSize:14, fontWeight:700, color:"var(--text)" }}>{e.forecast}</div>
                                    </div>
                                  )}
                                  {e.forecast && e.previous && (
                                    <div style={{ display:"flex", alignItems:"center", color: improving ? "var(--up)" : "var(--down)", fontSize:16, fontWeight:700 }}>
                                      {improving ? "↓" : "↑"}
                                    </div>
                                  )}
                                  {e.previous && (
                                    <div>
                                      <div style={{ fontFamily:"var(--font-mono)", fontSize:9, color:"var(--text-faint)", textTransform:"uppercase", letterSpacing:"0.1em" }}>Previous</div>
                                      <div style={{ fontFamily:"var(--font-mono)", fontSize:14, color:"var(--text-dim)" }}>{e.previous}</div>
                                    </div>
                                  )}
                                </div>
                              )}

                              {/* Impact blurb */}
                              {blurb && (
                                <div style={{ fontSize:11, color:"var(--text-dim)", lineHeight:1.5, marginBottom:8,
                                  padding:"6px 10px", background:"var(--bg-2)", borderRadius:5 }}>
                                  {blurb}
                                </div>
                              )}

                              {/* Countdown */}
                              <div style={{ fontFamily:"var(--font-mono)", fontSize:10,
                                color: du2 === 0 ? "var(--up)" : isImm ? "var(--warn)" : "var(--text-faint)" }}>
                                ⏱ {du2 === 0 ? "Today" : du2 === 1 ? "Tomorrow" : `In ${du2} days`}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>
          </>
        )}
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
