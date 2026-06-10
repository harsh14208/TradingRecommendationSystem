/* ─── Sources overlay ──────────────────────────────────────────────────────── */
function SourcesView({ open, onClose, sources, toggle }) {
  return (
    <div className={`overlay ${open?"open":""}`}>
      <div className="overlay-head">
        <div>
          <div className="crumb">SOURCES / INTEGRATIONS</div>
          <h2>Data feeds &amp; signal sources</h2>
        </div>
        <div style={{ marginLeft:"auto", display:"flex", gap:8 }}>
          <button className="btn ghost" onClick={onClose}><Icon name="x" size={14}/> Close</button>
        </div>
      </div>
      <div className="src-grid">
        {(sources||[]).map(s => (
          <div key={s.id} className="src-card">
            <div className="head">
              <div className="icon">{s.abbr}</div>
              <div style={{ minWidth:0 }}>
                <h3>{s.name}</h3>
                <div className="desc">{s.description}</div>
              </div>
              <div className={`toggle ${s.is_on?"on":""}`} onClick={() => toggle(s.id)} role="button" tabIndex={0}/>
            </div>
            <Sparkline ticker={s.id} up={s.is_on}/>
            <div className="stats">
              <div className="s"><span className="n">{(s.requests_24h||0).toLocaleString()}</span><span className="l">Requests 24h</span></div>
              <div className="s"><span className="n">{s.latency_ms||0}ms</span><span className="l">p50 latency</span></div>
              <div className="s"><span className="n" style={{ fontSize:11 }}>{s.feed||"—"}</span><span className="l">Cadence</span></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ─── Rules overlay ────────────────────────────────────────────────────────── */
const STYLE_INFO = {
  intraday: { label:"Intraday", hold:"Minutes to hours", horizon:"< 1 day",     chartTf:"1D / 5m" },
  swing:    { label:"Swing",    hold:"Days to weeks",    horizon:"2–10 days",    chartTf:"1M / 1H" },
  position: { label:"Position", hold:"Weeks to months",  horizon:"> 1 month",    chartTf:"1Y / 1D" },
};

function RulesView({ open, onClose, aggr, style, days, startTime, endTime, setTweak, customConf }) {
  const baseConf = aggr === "aggressive" ? 55 : aggr === "conservative" ? 75 : 65;
  const [confInput,    setConfInput]    = useState(String(customConf ?? baseConf));
  const [confError,    setConfError]    = useState("");
  const [rrInput,      setRrInput]      = useState(aggr === "aggressive" ? "1.5" : aggr === "conservative" ? "2.5" : "2.0");
  const [maxSigs,      setMaxSigs]      = useState(aggr === "aggressive" ? "12"  : aggr === "conservative" ? "4"   : "8");
  const [blockEarnings,setBlockEarnings]= useState(aggr === "conservative");
  const [timeError,    setTimeError]    = useState("");

  useEffect(() => {
    setConfInput(String(customConf ?? baseConf));
    setRrInput(aggr === "aggressive" ? "1.5" : aggr === "conservative" ? "2.5" : "2.0");
    setMaxSigs(aggr === "aggressive" ? "12"  : aggr === "conservative" ? "4"   : "8");
    setBlockEarnings(aggr === "conservative");
  }, [aggr]); // eslint-disable-line

  const saveConf = () => {
    const v = parseFloat(confInput);
    if (isNaN(v) || v < 0 || v > 100) {
      setConfError("Confidence must be 0–100");
      return;
    }
    setConfError("");
    setTweak({ customConf: v });
  };

  const validateAndSaveTime = (field, value) => {
    const t = value.trim();
    if (!/^\d{2}:\d{2}$/.test(t)) { setTimeError("Time must be HH:MM format"); return; }
    const [h, m] = t.split(":").map(Number);
    if (h > 23 || m > 59) { setTimeError("Invalid time"); return; }
    if (field === "endTime") {
      const start = startTime || "09:30";
      if (t <= start) { setTimeError("End time must be after start time"); return; }
    }
    if (field === "startTime") {
      const end = endTime || "16:00";
      if (t >= end) { setTimeError("Start time must be before end time"); return; }
    }
    setTimeError("");
    setTweak({ [field]: t });
  };

  const inp = { background:"var(--bg-2)", border:"1px solid var(--line)", borderRadius:4,
    color:"var(--text)", fontFamily:"var(--font-mono)", padding:"4px 8px", fontSize:14,
    fontWeight:600, width:"72px", outline:"none" };

  return (
    <div className={`overlay ${open?"open":""}`}>
      <div className="overlay-head">
        <div>
          <div className="crumb">RULES / SIGNAL FILTER</div>
          <h2>When to fire a signal</h2>
        </div>
        <button className="btn ghost" style={{ marginLeft:"auto" }} onClick={onClose}><Icon name="x" size={14}/> Close</button>
      </div>

      <div style={{ padding:"0 28px 16px" }}>
        <div style={{ fontSize:10, textTransform:"uppercase", letterSpacing:"0.14em", color:"var(--text-faint)", fontFamily:"var(--font-mono)", marginBottom:10 }}>Trading style</div>
        <div style={{ display:"grid", gridTemplateColumns:"repeat(3,1fr)", gap:10 }}>
          {["intraday","swing","position"].map(s => (
            <div key={s} className="src-card" onClick={() => setTweak({ style:s })} style={{ cursor:"pointer", borderColor:style===s?"var(--accent)":"var(--line)", background:style===s?"rgba(16,185,129,0.08)":"var(--bg-card)" }} role="button" tabIndex={0}>
              <div style={{ display:"flex", alignItems:"center", gap:8 }}>
                <span className={`style-badge ${s}`}>{s}</span>
                {style === s && <span style={{ marginLeft:"auto", fontSize:10, color:"var(--accent)", fontFamily:"var(--font-mono)" }}>✓ ACTIVE</span>}
              </div>
              <div style={{ fontSize:14, fontWeight:600, color:"var(--text)", marginTop:6 }}>{STYLE_INFO[s].label}</div>
              <div className="desc">{STYLE_INFO[s].hold}</div>
            </div>
          ))}
        </div>
      </div>

      <div style={{ padding:"8px 28px 20px", display:"grid", gridTemplateColumns:"repeat(auto-fill,minmax(240px,1fr))", gap:14 }}>

        <div className="src-card" style={{ gap:6 }}>
          <div style={{ fontSize:10, textTransform:"uppercase", letterSpacing:"0.1em", color:"var(--text-faint)", fontFamily:"var(--font-mono)" }}>Min Confidence</div>
          <div style={{ display:"flex", alignItems:"center", gap:6 }}>
            <input type="number" min={0} max={100} style={{ ...inp, borderColor: confError ? "var(--down)" : undefined }} value={confInput}
              onChange={e => { setConfInput(e.target.value); setConfError(""); }}
              onBlur={saveConf}
              onKeyDown={e => e.key === "Enter" && saveConf()}/>
            <span style={{ fontSize:16, fontWeight:600, color:"var(--accent)", fontFamily:"var(--font-mono)" }}>%</span>
          </div>
          {confError && <div style={{ fontSize:10, color:"var(--down)", fontFamily:"var(--font-mono)" }}>{confError}</div>}
          <div className="desc">Signals below this threshold are hidden from feed</div>
          <div style={{ fontSize:9, color:"var(--text-faint)", fontFamily:"var(--font-mono)", marginTop:2 }}>Press Enter or click away to apply</div>
        </div>

        <div className="src-card" style={{ gap:6 }}>
          <div style={{ fontSize:10, textTransform:"uppercase", letterSpacing:"0.1em", color:"var(--text-faint)", fontFamily:"var(--font-mono)" }}>Min R:R Ratio</div>
          <div style={{ display:"flex", alignItems:"center", gap:6 }}>
            <input type="number" min={0} max={10} step={0.1} style={inp} value={rrInput}
              onChange={e => setRrInput(e.target.value)}/>
          </div>
          <div className="desc">Reject setups below this reward-to-risk ratio</div>
        </div>

        <div className="src-card" style={{ gap:6 }}>
          <div style={{ fontSize:10, textTransform:"uppercase", letterSpacing:"0.1em", color:"var(--text-faint)", fontFamily:"var(--font-mono)" }}>Max Signals / Day</div>
          <input type="number" min={1} max={50} style={inp} value={maxSigs}
            onChange={e => setMaxSigs(e.target.value)}/>
          <div className="desc">Hard cap on Telegram sends per day</div>
        </div>

        <div className="src-card" style={{ gap:6 }}>
          <div style={{ fontSize:10, textTransform:"uppercase", letterSpacing:"0.1em", color:"var(--text-faint)", fontFamily:"var(--font-mono)" }}>Delivery Window (ET)</div>
          <div style={{ display:"flex", alignItems:"center", gap:6 }}>
            <input type="time" value={startTime||"09:30"}
              onChange={e => validateAndSaveTime("startTime", e.target.value)}
              style={{ ...inp, width:"80px", borderColor: timeError ? "var(--down)" : undefined }}/>
            <span style={{ color:"var(--text-faint)", fontFamily:"var(--font-mono)" }}>–</span>
            <input type="time" value={endTime||"16:00"}
              onChange={e => validateAndSaveTime("endTime", e.target.value)}
              style={{ ...inp, width:"80px", borderColor: timeError ? "var(--down)" : undefined }}/>
          </div>
          {timeError && <div style={{ fontSize:10, color:"var(--down)", fontFamily:"var(--font-mono)" }}>{timeError}</div>}
          <div className="desc">Sends suppressed outside this window</div>
        </div>

        <div className="src-card" style={{ gap:6 }}>
          <div style={{ fontSize:10, textTransform:"uppercase", letterSpacing:"0.1em", color:"var(--text-faint)", fontFamily:"var(--font-mono)" }}>24h Cooldown</div>
          <div className="mono" style={{ fontSize:20, fontWeight:600, color:"var(--accent)" }}>ON</div>
          <div className="desc">No duplicate ticker+action within 24h</div>
        </div>

        <div className="src-card" style={{ gap:6, cursor:"pointer" }}
          onClick={() => setBlockEarnings(v => !v)} role="button" tabIndex={0}>
          <div style={{ fontSize:10, textTransform:"uppercase", letterSpacing:"0.1em", color:"var(--text-faint)", fontFamily:"var(--font-mono)" }}>Block Pre-Earnings</div>
          <div className="mono" style={{ fontSize:20, fontWeight:600, color: blockEarnings ? "var(--accent)" : "var(--text-faint)" }}>
            {blockEarnings ? "ON" : "OFF"}
          </div>
          <div className="desc">Avoid earnings whipsaw (2-day hard blackout)</div>
          <div style={{ fontSize:9, color:"var(--text-faint)", fontFamily:"var(--font-mono)", marginTop:2 }}>Click to toggle</div>
        </div>

      </div>
    </div>
  );
}

/* ─── Outcome Strip (last N resolved outcomes for a ticker) ─────────────────── */
// OutcomeStrip accepts a precomputed map (outcomeByTicker) instead of the full
// history array to eliminate O(n*m) filter calls on every render.
// Falls back to filtering a legacy `history` array if map is not provided.
function OutcomeStrip({ ticker, outcomeByTicker, history }) {
  const resolved = outcomeByTicker
    ? (outcomeByTicker[ticker] || []).slice(0, 10)
    : (history || []).filter(h => h.ticker === ticker && h.outcomePct != null).slice(0, 10);
  if (resolved.length === 0) return null;
  const wins = resolved.filter(h => h.outcomePct > 0).length;
  return (
    <div style={{ display:"inline-flex", alignItems:"center", gap:4,
      padding:"3px 8px", fontFamily:"var(--font-mono)", fontSize:9,
      background:"var(--bg-1)", border:"1px solid var(--line)", borderRadius:6,
      color:"var(--text-faint)", marginLeft:"auto" }}
      title={`Last ${resolved.length} ${ticker} signals · ${wins}/${resolved.length} wins`}>
      <span style={{ letterSpacing:"0.12em", marginRight:2 }}>L{resolved.length}</span>
      {resolved.map((h, i) => {
        const win = h.outcomePct > 0;
        // colour-code by exit type when available
        const exitColor = h.exitType === "target" ? "var(--up)"
                        : h.exitType === "stop"   ? "var(--down)"
                        : h.exitType === "time"   ? "var(--warn)"
                        : win ? "var(--up)" : "var(--down)";
        const tip = h.exitType ? `${h.exitType.toUpperCase()} exit · ${h.outcomePct > 0 ? "+" : ""}${h.outcomePct?.toFixed(2)}%` : undefined;
        return (
          <span key={i} title={tip} style={{
            width:6, height:6, borderRadius:"50%",
            background: exitColor,
            boxShadow: win ? `0 0 4px color-mix(in oklch,${exitColor} 60%,transparent)` : undefined,
          }}/>
        );
      })}
      <span style={{ color:"var(--text)", fontSize:10, marginLeft:4 }}>
        {Math.round(wins / resolved.length * 100)}%
      </span>
    </div>
  );
}

/* ─── History overlay ───────────────────────────────────────────────────────── */
function HistoryView({ open, onClose, online }) {
  const [rows,      setRows]      = useState([]);
  const [loading,   setLoading]   = useState(false);
  const [startDate, setStartDate] = useState("");
  const [endDate,   setEndDate]   = useState("");
  const [tickerQ,   setTickerQ]   = useState("");
  const [actionQ,   setActionQ]   = useState("");
  const [outcomeQ,  setOutcomeQ]  = useState("");

  const loadHistory = (sd, ed, tk, ac, oc, signal) => {
    if (!online) return;
    setLoading(true);
    const params = new URLSearchParams();
    if (sd) params.set("start_date", sd);
    if (ed) params.set("end_date",   ed);
    if (tk) params.set("ticker",     tk.toUpperCase().trim());
    if (ac) params.set("action",     ac);
    if (oc) params.set("outcome",    oc);
    const qs = params.toString() ? `?${params}` : "";
    apiFetch(`/api/signals/history${qs}`, { signal }).then(d => {
      setRows(Array.isArray(d) ? d : []);
      setLoading(false);
    }).catch(() => setLoading(false));
  };

  const applyFilters = () => loadHistory(startDate, endDate, tickerQ, actionQ, outcomeQ);
  const clearFilters = () => {
    setStartDate(""); setEndDate(""); setTickerQ(""); setActionQ(""); setOutcomeQ("");
    loadHistory("","","","","");
  };

  useEffect(() => {
    if (!open) return;
    const ctrl = new AbortController();
    loadHistory(startDate, endDate, tickerQ, actionQ, outcomeQ, ctrl.signal);
    return () => ctrl.abort();
  }, [open, online, startDate, endDate, tickerQ, actionQ, outcomeQ]);

  const fmtRet = v => v == null ? "—" : `${v >= 0 ? "+" : ""}${v.toFixed(2)}%`;
  const retColor = v => v == null ? "var(--text-faint)" : v >= 0 ? "var(--up)" : "var(--down)";

  const exitBadge = r => {
    if (!r.exitType) return null;
    const cfg = { target:["TARGET","var(--up)"], stop:["STOP","var(--down)"], time:["TIME","var(--warn)"], pending:["OPEN","var(--text-faint)"] };
    const [lbl, col] = cfg[r.exitType] || ["—","var(--text-faint)"];
    return <span style={{ fontSize:9, fontFamily:"var(--font-mono)", fontWeight:700, padding:"2px 5px", borderRadius:3,
      color:col, background:`color-mix(in oklch,${col} 12%,transparent)` }}>{lbl}</span>;
  };

  const exportCSV = () => {
    const headers = ["Date","Ticker","Action","Confidence","Price","1d","3d","7d","14d","MAE","MFE","Exit"];
    const csvRows = [
      headers.join(","),
      ...rows.map(r => [
        fmtETFull(r.ts),
        r.ticker,
        r.action,
        r.confidence?.toFixed(0) ?? "",
        r.price,
        fmtRet(r.outcome1d),
        fmtRet(r.outcome3d),
        fmtRet(r.outcomePct),
        fmtRet(r.outcome14d),
        r.mae != null ? `${r.mae.toFixed(2)}%` : "",
        r.mfe != null ? `${r.mfe.toFixed(2)}%` : "",
        r.exitType ?? "",
      ].map(v => `"${String(v).replace(/"/g,'""')}"`).join(",")),
    ];
    const blob = new Blob([csvRows.join("\n")], { type:"text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = `signal-history-${new Date().toISOString().slice(0,10)}.csv`;
    a.click(); URL.revokeObjectURL(url);
  };

  const dateInputStyle = {
    background:"var(--bg-card,var(--bg-2))", border:"1px solid var(--line)",
    borderRadius:4, color:"var(--text)", padding:"5px 8px",
    fontFamily:"var(--font-mono)", fontSize:11,
  };

  return (
    <div className={`overlay ${open?"open":""}`}>
      <div className="overlay-head" style={{ flexWrap:"wrap", rowGap:8 }}>
        <div>
          <div className="crumb">ARCHIVE / HISTORY</div>
          <h2>Signal history</h2>
        </div>
        <div style={{ display:"flex", alignItems:"center", gap:8, fontFamily:"var(--font-mono)", fontSize:11, flexWrap:"wrap" }}>
          <input placeholder="TICKER" value={tickerQ} onChange={e => setTickerQ(e.target.value)}
            style={{ ...dateInputStyle, width:72, textTransform:"uppercase" }}/>
          <select value={actionQ} onChange={e => setActionQ(e.target.value)} style={{ ...dateInputStyle, cursor:"pointer" }}>
            <option value="">All actions</option>
            <option value="BUY">BUY</option>
            <option value="SELL">SELL</option>
            <option value="HOLD">HOLD</option>
          </select>
          <select value={outcomeQ} onChange={e => setOutcomeQ(e.target.value)} style={{ ...dateInputStyle, cursor:"pointer" }}>
            <option value="">All outcomes</option>
            <option value="win">Wins</option>
            <option value="loss">Losses</option>
            <option value="open">Open</option>
          </select>
          <span style={{ color:"var(--text-faint)", letterSpacing:"0.08em" }}>FROM</span>
          <input type="date" style={dateInputStyle} value={startDate} onChange={e => setStartDate(e.target.value)}/>
          <span style={{ color:"var(--text-faint)" }}>–</span>
          <input type="date" style={dateInputStyle} value={endDate} onChange={e => setEndDate(e.target.value)}/>
          <button className="btn" style={{ fontSize:11, padding:"5px 12px" }} onClick={applyFilters}>Apply</button>
          {(startDate || endDate || tickerQ || actionQ || outcomeQ) && (
            <button className="btn ghost" style={{ fontSize:11 }} onClick={clearFilters}>Clear</button>
          )}
        </div>
        <div style={{ marginLeft:"auto", display:"flex", gap:8 }}>
          {rows.length > 0 && (
            <button className="btn ghost" style={{ fontSize:11 }} onClick={exportCSV}>
              ↓ Export CSV
            </button>
          )}
          <button className="btn ghost" onClick={onClose}><Icon name="x" size={14}/> Close</button>
        </div>
      </div>
      <div style={{ padding:"0 28px 28px", overflowY:"auto", maxHeight:"calc(100vh - 120px)" }}>
        {loading && <div style={{ padding:"40px 0", textAlign:"center", color:"var(--text-faint)", fontSize:12 }}>Loading…</div>}
        {!loading && rows.length === 0 && <div style={{ padding:"40px 0", textAlign:"center", color:"var(--text-faint)", fontSize:12 }}>No history yet.</div>}
        {rows.length > 0 && (
          <SortableTable
            cols={["Date","Ticker","Action","Conf","Price","Exit","Return","MAE","MFE","1d","3d"]}
            defaultSort={{ col:0, dir:"desc" }}
            rows={rows.slice(0,200).map(r => {
              // Exit type is now the PRIMARY outcome column.
              // Raw % return is shown as secondary. This matches reality: a signal
              // that hit its stop at -8% and recovered to +1% at day 7 is a LOSS.
              const exitType = r.exitType;
              const primaryRet = r.outcome14d ?? r.outcomePct ?? r.outcome3d ?? r.outcome1d;
              const exitPrimary = exitBadge(r);
              const retDisplay = exitPrimary
                ? <span style={{ fontFamily:"var(--font-mono)", fontSize:11,
                    color: exitType === "target" ? "var(--up)" : exitType === "stop" ? "var(--down)" : retColor(primaryRet) }}>
                    {primaryRet != null ? fmtRet(primaryRet) : "—"}
                  </span>
                : <span style={{ color:retColor(primaryRet) }}>{fmtRet(primaryRet)}</span>;
              return [
                fmtETFull(r.ts),
                r.ticker,
                <span className={`signal-verb ${r.action}`} style={{ fontSize:10 }}>{r.action}</span>,
                `${r.confidence?.toFixed(0)}%`,
                `$${fmt(r.price)}`,
                exitPrimary ?? <span style={{ color:"var(--text-faint)", fontSize:10 }}>pending</span>,
                retDisplay,
                r.mae != null ? <span title="Max Adverse Excursion" style={{ color:"var(--down)" }}>{r.mae.toFixed(2)}%</span> : "—",
                r.mfe != null ? <span title="Max Favorable Excursion" style={{ color:"var(--up)" }}>+{r.mfe.toFixed(2)}%</span> : "—",
                fmtRet(r.outcome1d),
                fmtRet(r.outcome3d),
              ];
            })}
            colors={[
              null, null, null,
              () => "var(--accent)",
              null, null,
              (_,ri) => { const r = rows[ri]; return r?.exitType === "target" ? "var(--up)" : r?.exitType === "stop" ? "var(--down)" : retColor(r?.outcomePct); },
              () => "var(--down)",
              () => "var(--up)",
              (_,ri) => retColor(rows[ri]?.outcome1d),
              (_,ri) => retColor(rows[ri]?.outcome3d),
            ]}/>
        )}
      </div>
    </div>
  );
}

/* ─── My Performance overlay ──────────────────────────────────────────────── */
function MyPerformanceView({ open, onClose }) {
  const [data,    setData]    = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!open) return;
    setLoading(true);
    apiFetch("/api/me/performance?limit=100")
      .then(d => { setData(d); setLoading(false); })
      .catch(() => setLoading(false));
  }, [open]);

  const fmtRet = v => v == null ? "—" : `${v >= 0 ? "+" : ""}${v.toFixed(2)}%`;
  const retColor = v => v == null ? "var(--text-faint)" : v >= 0 ? "var(--up)" : "var(--down)";

  const statCard = (label, value, sub) => (
    <div style={{ background:"var(--bg-2)", borderRadius:8, padding:"12px 16px", minWidth:100 }}>
      <div style={{ fontSize:10, color:"var(--text-faint)", fontFamily:"var(--font-mono)", textTransform:"uppercase", letterSpacing:"0.1em", marginBottom:4 }}>{label}</div>
      <div style={{ fontSize:20, fontWeight:700, color:"var(--text)", fontFamily:"var(--font-mono)" }}>{value ?? "—"}</div>
      {sub && <div style={{ fontSize:10, color:"var(--text-faint)", marginTop:2 }}>{sub}</div>}
    </div>
  );

  const stats = data?.stats;
  const recent = data?.recent || [];

  return (
    <div className={`overlay ${open ? "open" : ""}`}>
      <div className="overlay-head">
        <div>
          <div className="crumb">ACCOUNT / PERFORMANCE</div>
          <h2>My signal performance</h2>
        </div>
        <button className="close-btn" onClick={onClose}>×</button>
      </div>

      <div style={{ padding:"20px 24px", overflowY:"auto", flex:1 }}>
        {loading ? (
          <div style={{ color:"var(--text-faint)", fontSize:13, textAlign:"center", paddingTop:40 }}>Loading…</div>
        ) : !data ? (
          <div style={{ color:"var(--text-faint)", fontSize:13, textAlign:"center", paddingTop:40 }}>No data available</div>
        ) : (
          <>
            {/* Stats row */}
            <div style={{ display:"flex", gap:12, flexWrap:"wrap", marginBottom:24 }}>
              {statCard("Delivered", stats.delivered, "signals sent to you")}
              {statCard("Resolved", stats.resolved, `${stats.pending} pending`)}
              {statCard("Win rate", stats.win_rate != null ? `${stats.win_rate}%` : null, `${stats.wins}W / ${stats.losses}L`)}
              {statCard("Avg return", stats.avg_return != null ? fmtRet(stats.avg_return) : null, "per trade")}
              {stats.sharpe != null && statCard("Sharpe", stats.sharpe, "annualised est.")}
            </div>

            {/* Signal list */}
            {recent.length === 0 ? (
              <div style={{ color:"var(--text-faint)", fontSize:13, textAlign:"center", paddingTop:20 }}>
                No signals have been delivered to your account yet.
              </div>
            ) : (
              <div style={{ overflowX:"auto" }}>
                <table style={{ width:"100%", borderCollapse:"collapse", fontSize:12 }}>
                  <thead>
                    <tr style={{ borderBottom:"1px solid var(--line)", color:"var(--text-faint)", fontFamily:"var(--font-mono)", fontSize:10 }}>
                      <th style={{ textAlign:"left", padding:"6px 8px" }}>Date</th>
                      <th style={{ textAlign:"left", padding:"6px 8px" }}>Ticker</th>
                      <th style={{ textAlign:"left", padding:"6px 8px" }}>Action</th>
                      <th style={{ textAlign:"right", padding:"6px 8px" }}>Conf</th>
                      <th style={{ textAlign:"right", padding:"6px 8px" }}>Price</th>
                      <th style={{ textAlign:"right", padding:"6px 8px" }}>Return</th>
                      <th style={{ textAlign:"left", padding:"6px 8px" }}>Exit</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recent.map(r => {
                      const exitCfg = { target:["TARGET","var(--up)"], stop:["STOP","var(--down)"], time:["TIME","var(--warn)"], pending:["OPEN","var(--text-faint)"] };
                      const [exitLbl, exitCol] = (r.exit_type && exitCfg[r.exit_type]) || ["—","var(--text-faint)"];
                      const isWin = r.outcome_pct > 0;
                      const isLoss = r.outcome_pct != null && r.outcome_pct <= 0;
                      return (
                        <tr key={r.id} style={{ borderBottom:"1px solid color-mix(in oklch, var(--line) 50%, transparent)" }}>
                          <td style={{ padding:"8px 8px", color:"var(--text-faint)", fontFamily:"var(--font-mono)", fontSize:11 }}>
                            {r.sent_at ? r.sent_at.slice(0,10) : (r.created_at ? r.created_at.slice(0,10) : "—")}
                          </td>
                          <td style={{ padding:"8px 8px", fontWeight:700 }}>{r.ticker}</td>
                          <td style={{ padding:"8px 8px" }}>
                            <span style={{ fontSize:10, fontWeight:700, fontFamily:"var(--font-mono)", color: r.action === "BUY" ? "var(--up)" : "var(--down)" }}>
                              {r.action}
                            </span>
                          </td>
                          <td style={{ padding:"8px 8px", textAlign:"right", fontFamily:"var(--font-mono)", color:"var(--text-faint)", fontSize:11 }}>{r.confidence?.toFixed(0)}%</td>
                          <td style={{ padding:"8px 8px", textAlign:"right", fontFamily:"var(--font-mono)", fontSize:11 }}>${r.price?.toFixed(2)}</td>
                          <td style={{ padding:"8px 8px", textAlign:"right", fontFamily:"var(--font-mono)", fontWeight:600,
                            color: r.outcome_pct == null ? "var(--text-faint)" : retColor(r.outcome_pct) }}>
                            {fmtRet(r.outcome_pct)}
                          </td>
                          <td style={{ padding:"8px 8px" }}>
                            {r.exit_type ? (
                              <span style={{ fontSize:10, fontFamily:"var(--font-mono)", fontWeight:700, padding:"2px 5px", borderRadius:3,
                                color:exitCol, background:`color-mix(in oklch,${exitCol} 12%,transparent)` }}>{exitLbl}</span>
                            ) : <span style={{ color:"var(--text-faint)", fontSize:11 }}>—</span>}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

/* ─── Backtest overlay ──────────────────────────────────────────────────────── */
// btCache / onBtCache: parent-supplied cache so results survive close/reopen.
// Cache TTL is 10 minutes — avoids 8 expensive GROUP BY queries on every open.
const BT_CACHE_TTL_MS = 10 * 60 * 1000;

function BacktestView({ open, onClose, online, btCache, onBtCache }) {
  const [tab,       setTab]       = useState("summary");
  const [data,      setData]      = useState(null);
  const [horizons,  setHorizons]  = useState([]);
  const [accuracy,  setAccuracy]  = useState({ sources: null, tickers: null });
  const [trackRec,  setTrackRec]  = useState(null);
  const [corr,      setCorr]      = useState(null);
  const [calib,     setCalib]     = useState(null);
  const [decay,     setDecay]     = useState(null);
  const [loading,   setLoading]   = useState(false);
  const [backfilling,    setBackfilling]    = useState(false);
  const [backfillResult, setBackfillResult] = useState(null);
  const [startDate, setStartDate] = useState("");
  const [endDate,   setEndDate]   = useState("");

  const load = (sd, ed, force = false, signal) => {
    if (!online) return;
    // Use parent cache if fresh and no date filters are active
    if (!force && !sd && !ed && btCache && (Date.now() - btCache.ts) < BT_CACHE_TTL_MS) {
      const c = btCache;
      setData(c.data); setHorizons(c.horizons); setAccuracy(c.accuracy);
      setTrackRec(c.trackRec); setCorr(c.corr); setCalib(c.calib); setDecay(c.decay);
      return;
    }
    setLoading(true);
    const params = new URLSearchParams();
    if (sd) params.set("start_date", sd);
    if (ed) params.set("end_date",   ed);
    const qs = params.toString() ? `?${params}` : "";
    Promise.all([
      apiFetch(`/api/signals/backtest${qs}`, { signal }),
      apiFetch(`/api/signals/backtest/horizons${qs}`, { signal }),
      apiFetch("/api/accuracy/sources", { signal }),
      apiFetch("/api/accuracy/tickers", { signal }),
      apiFetch("/api/signals/track-record", { signal }),
      apiFetch("/api/signals/correlation", { signal }),
      apiFetch(`/api/signals/backtest/calibration${qs}`, { signal }),
      apiFetch("/api/signals/alpha-decay", { signal }),
    ]).then(([d, h, src, tkr, tr, cr, cal, dc]) => {
      const next = {
        ts: Date.now(), data: d, horizons: (h||[]).filter(h => h.n > 0),
        accuracy: { sources: src || [], tickers: tkr || [] },
        trackRec: tr || [], corr: cr, calib: cal || [], decay: dc || {},
      };
      setData(next.data); setHorizons(next.horizons); setAccuracy(next.accuracy);
      setTrackRec(next.trackRec); setCorr(next.corr); setCalib(next.calib); setDecay(next.decay);
      if (!sd && !ed && onBtCache) onBtCache(next);
      setLoading(false);
    }).catch(() => setLoading(false));
  };

  useEffect(() => {
    if (!open) return;
    const ctrl = new AbortController();
    load(startDate, endDate, false, ctrl.signal);
    return () => ctrl.abort();
  }, [open, online, startDate, endDate, btCache, onBtCache]);

  const runBackfill = () => {
    setBackfilling(true);
    authFetch("/api/signals/backtest/backfill", { method:"POST" })
      .then(r => r.json())
      .then(r => { setBackfillResult(r); setBackfilling(false); load(); })
      .catch(() => setBackfilling(false));
  };

  const fmtPct = v => v == null ? "—" : `${v >= 0 ? "+" : ""}${v.toFixed(2)}%`;
  const fmtWr  = v => v == null ? "—" : `${v.toFixed(1)}%`;
  const wrColor  = v => v == null ? "var(--text-faint)" : v >= 60 ? "var(--up)" : v >= 45 ? "var(--warn)" : "var(--down)";
  const retColor = v => v == null ? "var(--text-faint)" : v >= 0 ? "var(--up)" : "var(--down)";

  return (
    <div className={`overlay ${open?"open":""}`}>
      <div className="overlay-head" style={{ flexWrap:"wrap", rowGap:8 }}>
        <div>
          <div className="crumb">ARCHIVE / BACKTESTING</div>
          <h2>Win-rate analytics</h2>
        </div>
        <div style={{ display:"flex", alignItems:"center", gap:8, fontFamily:"var(--font-mono)", fontSize:11 }}>
          <span style={{ color:"var(--text-faint)", letterSpacing:"0.08em" }}>FROM</span>
          <input type="date" value={startDate} onChange={e => setStartDate(e.target.value)}
            style={{ background:"var(--bg-2)", border:"1px solid var(--line)", borderRadius:4,
              color:"var(--text)", padding:"5px 8px", fontFamily:"var(--font-mono)", fontSize:11 }}/>
          <span style={{ color:"var(--text-faint)" }}>–</span>
          <input type="date" value={endDate} onChange={e => setEndDate(e.target.value)}
            style={{ background:"var(--bg-2)", border:"1px solid var(--line)", borderRadius:4,
              color:"var(--text)", padding:"5px 8px", fontFamily:"var(--font-mono)", fontSize:11 }}/>
          <button className="btn" style={{ fontSize:11, padding:"5px 12px" }}
            onClick={() => load(startDate, endDate)}>Apply</button>
          {(startDate || endDate) && (
            <button className="btn ghost" style={{ fontSize:11 }}
              onClick={() => { setStartDate(""); setEndDate(""); load("",""); }}>Clear</button>
          )}
        </div>
        <div style={{ marginLeft:"auto", display:"flex", gap:10, alignItems:"center" }}>
          <button className="btn ghost" style={{ fontSize:11 }} onClick={runBackfill} disabled={backfilling || !online}>
            {backfilling ? "Backfilling…" : "Backfill Outcomes"}
          </button>
          <button className="btn ghost" onClick={onClose}><Icon name="x" size={14}/> Close</button>
        </div>
      </div>
      <div style={{ display:"flex", gap:0, borderBottom:"1px solid var(--line)", padding:"0 28px", background:"var(--bg-1)" }}>
        {[["summary","Summary"],["sources","By Source"],["tickers","By Ticker"],["track","Track Record"],["corr","Correlation"],["calib","Calibration"],["decay","Alpha Decay"],["model","ML Model"]].map(([id,label]) => (
          <button key={id} onClick={() => setTab(id)}
            style={{ padding:"10px 14px", fontSize:11, fontFamily:"var(--font-mono)", fontWeight:600, letterSpacing:"0.06em", textTransform:"uppercase", background:"none", border:"none", cursor:"pointer", borderBottom: tab===id ? "2px solid var(--accent)" : "2px solid transparent", color: tab===id ? "var(--accent)" : "var(--text-faint)", marginBottom:-1 }}>
            {label}
          </button>
        ))}
      </div>

      <div style={{ padding:"0 28px 28px", overflowY:"auto", maxHeight:"calc(100vh - 160px)" }}>
        {backfillResult && (
          <div style={{ margin:"12px 0", padding:"10px 16px", borderRadius:8, background:"rgba(16,185,129,0.1)", border:"1px solid var(--accent)", fontSize:12, display:"flex", justifyContent:"space-between" }}>
            <span style={{ color:"var(--accent)" }}>{backfillResult.message}</span>
            <button onClick={() => setBackfillResult(null)} style={{ background:"none", border:"none", cursor:"pointer", color:"var(--text-faint)", fontSize:16 }}>×</button>
          </div>
        )}
        {loading && <div style={{ padding:"40px 0", textAlign:"center", color:"var(--text-faint)", fontSize:12 }}>Loading…</div>}

        {!loading && tab === "summary" && (data ? (
          <div style={{ display:"flex", flexDirection:"column", gap:24, paddingTop:20 }}>
            <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fill,minmax(150px,1fr))", gap:12 }}>
              {[
                ["Signals", data.resolved, "var(--text)"],
                ["Win rate", fmtWr(data.win_rate), wrColor(data.win_rate)],
                ["Avg return", fmtPct(data.avg_return), retColor(data.avg_return)],
                ["Sharpe", data.sharpe ?? "—", (data.sharpe||0) >= 1 ? "var(--up)" : "var(--text)"],
              ].map(([l,v,c]) => (
                <div key={l} style={{ background:"var(--bg-2)", borderRadius:8, padding:"14px 16px" }}>
                  <div style={{ fontSize:10, color:"var(--text-faint)", fontFamily:"var(--font-mono)", textTransform:"uppercase", letterSpacing:"0.08em", marginBottom:6 }}>{l}</div>
                  <div style={{ fontSize:22, fontWeight:700, fontFamily:"var(--font-mono)", color:c }}>{v}</div>
                </div>
              ))}
            </div>
            {horizons.length > 0 && (
              <div>
                <div style={{ fontSize:11, fontWeight:600, color:"var(--text-dim)", textTransform:"uppercase", letterSpacing:"0.08em", marginBottom:10 }}>By hold period</div>
                <div style={{ display:"grid", gridTemplateColumns:`repeat(${horizons.length},1fr)`, gap:10 }}>
                  {horizons.map(h => (
                    <div key={h.horizon} style={{ background:"var(--bg-2)", borderRadius:8, padding:"12px 14px", border:"1px solid var(--line)" }}>
                      <div style={{ fontSize:10, fontFamily:"var(--font-mono)", color:"var(--text-faint)", textTransform:"uppercase", marginBottom:6 }}>{h.horizon} · {h.n} signals</div>
                      <div style={{ fontSize:18, fontWeight:700, fontFamily:"var(--font-mono)", color:wrColor(h.win_rate) }}>{fmtWr(h.win_rate)}</div>
                      <div style={{ fontSize:12, color:retColor(h.avg_return), fontFamily:"var(--font-mono)" }}>{fmtPct(h.avg_return)} avg</div>
                      <div style={{ marginTop:8, height:3, borderRadius:2, background:"var(--line)", overflow:"hidden" }}>
                        <div style={{ height:"100%", width:`${h.win_rate ?? 0}%`, borderRadius:2, background:wrColor(h.win_rate) }}/>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {data.by_action?.length > 0 && (
              <BtTable title="By signal direction" cols={["Direction","Signals","Win Rate","Avg Return","Avg Win","Avg Loss"]}
                rows={data.by_action.map(r => [
                  <span className={`signal-verb ${r.action}`} style={{ fontSize:10 }}>{r.action}</span>,
                  r.count, fmtWr(r.win_rate), fmtPct(r.avg_return), fmtPct(r.avg_win), fmtPct(r.avg_loss)
                ])}
                colors={[null,null,r=>wrColor(data.by_action[r]?.win_rate),r=>retColor(data.by_action[r]?.avg_return),"var(--up)","var(--down)"]}/>
            )}
          </div>
        ) : (
          <div style={{ padding:"60px 0", textAlign:"center", color:"var(--text-faint)", fontSize:12, lineHeight:1.8 }}>
            No resolved signals yet.<br/>
            <button className="btn primary" style={{ marginTop:14, fontSize:12 }} onClick={runBackfill} disabled={backfilling}>
              {backfilling ? "Backfilling…" : "Backfill from Historical Prices"}
            </button>
          </div>
        ))}

        {!loading && tab === "sources" && (
          <div style={{ paddingTop:20 }}>
            {accuracy.sources?.length > 0 ? (
              <BtTable title="Win rate by data source" cols={["Source","Signals","Win Rate","Avg Return"]}
                rows={accuracy.sources.map(r => [r.source, r.total, fmtWr(r.win_rate), fmtPct(r.avg_ret)])}
                colors={[null,null,(_,r)=>wrColor(accuracy.sources[r]?.win_rate),(_,r)=>retColor(accuracy.sources[r]?.avg_ret)]}/>
            ) : <EmptyBt msg="No source accuracy data yet. Backfill outcomes first."/>}
          </div>
        )}

        {!loading && tab === "tickers" && (
          <div style={{ paddingTop:20 }}>
            {accuracy.tickers?.length > 0 ? (
              <BtTable title="Win rate by ticker" cols={["Ticker","Signals","Win Rate","Avg Return","Top Sources"]}
                rows={accuracy.tickers.map(r => [r.ticker, r.total, fmtWr(r.win_rate), fmtPct(r.avg_ret), (r.top_sources||[]).join(", ")])}
                colors={[null,null,(_,r)=>wrColor(accuracy.tickers[r]?.win_rate),(_,r)=>retColor(accuracy.tickers[r]?.avg_ret),null]}/>
            ) : <EmptyBt msg="No ticker accuracy data yet. Backfill outcomes first."/>}
          </div>
        )}

        {!loading && tab === "track" && (
          <div style={{ paddingTop:20 }}>
            {trackRec?.length > 0 ? (
              <BtTable title="Per-ticker track record" cols={["Ticker","Signals","Win Rate","Avg Return","Sharpe"]}
                rows={trackRec.map(r => [r.ticker, r.signals ?? r.total, fmtWr(r.win_rate), fmtPct(r.avg_return), r.sharpe?.toFixed(2) ?? "—"])}
                colors={[null,null,(_,r)=>wrColor(trackRec[r]?.win_rate),(_,r)=>retColor(trackRec[r]?.avg_return),null]}/>
            ) : <EmptyBt msg="No resolved signals per ticker yet. Backfill outcomes first."/>}
          </div>
        )}

        {!loading && tab === "corr" && (
          <div style={{ paddingTop:20 }}>
            {(corr?.pairs ?? corr)?.length > 0 ? (
              <BtTable title="Source co-occurrence · joint win rates" cols={["Source A","Source B","Joint Signals","Joint Win Rate"]}
                rows={(corr?.pairs ?? corr).map(r => [r.a ?? r.source_a, r.b ?? r.source_b, r.count, fmtWr(r.win_rate)])}
                colors={[null,null,null,(_,r)=>wrColor((corr?.pairs??corr)[r]?.win_rate)]}/>
            ) : <EmptyBt msg="No correlation data yet. Backfill outcomes first."/>}
          </div>
        )}

        {!loading && tab === "calib" && (
          <div style={{ paddingTop:20 }}>
            {calib && calib.length > 0 ? (
              <div style={{ display:"flex", flexDirection:"column", gap:24 }}>
                <div>
                  <div style={{ fontSize:11, fontWeight:600, color:"var(--text-dim)", textTransform:"uppercase", letterSpacing:"0.08em", marginBottom:4 }}>Signal Confidence Calibration</div>
                  <div style={{ fontSize:11, color:"var(--text-faint)", marginBottom:16 }}>
                    Each bar shows the predicted confidence vs actual win rate. A well-calibrated model has bars near the diagonal.
                    Bars above the line = overconfident. Bars below = underconfident.
                  </div>
                  <CalibrationChart data={calib} />
                </div>
                <BtTable title="Calibration by confidence bucket"
                  cols={["Bucket","Predicted","Actual Win Rate","Signals","Gap"]}
                  rows={calib.map(r => [
                    r.bucket,
                    `${r.predicted.toFixed(1)}%`,
                    fmtWr(r.actual),
                    r.count,
                    <span style={{ color: Math.abs(r.gap) > 10 ? "var(--down)" : Math.abs(r.gap) > 5 ? "var(--warn)" : "var(--up)" }}>
                      {r.gap > 0 ? `+${r.gap.toFixed(1)}%` : `${r.gap.toFixed(1)}%`}
                    </span>
                  ])}
                  colors={[null,null,(_,ri)=>wrColor(calib[ri]?.actual),null,null]}/>
              </div>
            ) : <EmptyBt msg="No calibration data yet. Backfill outcomes first, then return here." />}
          </div>
        )}

        {!loading && tab === "decay" && (
          <div style={{ paddingTop:20 }}>
            <div style={{ fontSize:11, color:"var(--text-faint)", marginBottom:16, maxWidth:620 }}>
              Alpha decay by signal source — win rate and average return at each holding horizon.
              Sources that peak at 1d are short-lived; sources still strong at 14d have durable edge.
              Use this to inform which signal families warrant longer holds.
            </div>
            {decay && Object.keys(decay).length > 0 ? (
              <BtTable
                title="Alpha decay by source"
                cols={["Source","N","1d Win%","1d Ret","3d Win%","3d Ret","7d Win%","7d Ret","14d Win%","14d Ret"]}
                rows={Object.entries(decay)
                  .sort((a,b) => (b[1].h7d?.win_rate ?? 0) - (a[1].h7d?.win_rate ?? 0))
                  .map(([src, d]) => {
                    const h = h => d[h];
                    const wr = v => v?.win_rate != null ? `${v.win_rate.toFixed(1)}%` : "—";
                    const ret = v => v?.avg_ret != null ? `${v.avg_ret >= 0 ? "+" : ""}${v.avg_ret.toFixed(2)}%` : "—";
                    return [
                      src,
                      d.n,
                      wr(h("h1d")), ret(h("h1d")),
                      wr(h("h3d")), ret(h("h3d")),
                      wr(h("h7d")), ret(h("h7d")),
                      wr(h("h14d")), ret(h("h14d")),
                    ];
                  })}
                colors={[
                  null, null,
                  (_,ri) => { const v = Object.values(decay)[ri]?.h1d?.win_rate; return v != null ? wrColor(v) : "var(--text-faint)"; },
                  (_,ri) => { const v = Object.values(decay)[ri]?.h1d?.avg_ret;  return v != null ? (v>=0?"var(--up)":"var(--down)") : "var(--text-faint)"; },
                  (_,ri) => { const v = Object.values(decay)[ri]?.h3d?.win_rate; return v != null ? wrColor(v) : "var(--text-faint)"; },
                  (_,ri) => { const v = Object.values(decay)[ri]?.h3d?.avg_ret;  return v != null ? (v>=0?"var(--up)":"var(--down)") : "var(--text-faint)"; },
                  (_,ri) => { const v = Object.values(decay)[ri]?.h7d?.win_rate; return v != null ? wrColor(v) : "var(--text-faint)"; },
                  (_,ri) => { const v = Object.values(decay)[ri]?.h7d?.avg_ret;  return v != null ? (v>=0?"var(--up)":"var(--down)") : "var(--text-faint)"; },
                  (_,ri) => { const v = Object.values(decay)[ri]?.h14d?.win_rate; return v != null ? wrColor(v) : "var(--text-faint)"; },
                  (_,ri) => { const v = Object.values(decay)[ri]?.h14d?.avg_ret;  return v != null ? (v>=0?"var(--up)":"var(--down)") : "var(--text-faint)"; },
                ]}/>
            ) : <EmptyBt msg="No alpha decay data yet. Backfill outcomes first, then return here." />}
          </div>
        )}

        {!loading && tab === "model" && <MLModelTab online={online}/>}
      </div>
    </div>
  );
}

/* ─── ML Model feature-importance tab ───────────────────────────────────────── */
function MLModelTab({ online }) {
  const [mlData, setMlData]   = useState(null);
  const [mlLoad, setMlLoad]   = useState(false);
  const [mlErr,  setMlErr]    = useState("");
  const [training, setTraining] = useState(false);
  const [trainMsg, setTrainMsg] = useState("");

  useEffect(() => {
    if (!online) return;
    setMlLoad(true);
    const ctrl = new AbortController();
    apiFetch("/api/ml/status", { signal: ctrl.signal })
      .then(d => { setMlData(d); setMlLoad(false); })
      .catch(() => { setMlErr("Could not load ML model status."); setMlLoad(false); });
    return () => ctrl.abort();
  }, [online]);

  const triggerTrain = async () => {
    setTraining(true); setTrainMsg("");
    try {
      const d = await apiFetch("/api/ml/train", { method:"POST" });
      setMlData(d);
      setTrainMsg("Model retrained successfully.");
    } catch (e) {
      setTrainMsg("Training failed — " + (e?.message || "check server logs"));
    } finally { setTraining(false); }
  };

  if (mlLoad) return <div style={{ padding:"40px 0", textAlign:"center", color:"var(--text-faint)", fontSize:12 }}>Loading model status…</div>;
  if (mlErr)  return <div style={{ padding:20, color:"var(--down)", fontSize:12 }}>{mlErr}</div>;
  if (!mlData) return null;

  const fi = mlData.feature_importances || [];
  const maxImp = fi.length > 0 ? Math.max(...fi.map(f => f.importance || 0)) : 1;

  return (
    <div style={{ paddingTop:20, maxWidth:680 }}>
      {/* ── Status header ── */}
      <div style={{ display:"flex", gap:16, marginBottom:20, flexWrap:"wrap" }}>
        {[
          ["Status",      mlData.model_exists ? "Trained" : "Not trained", mlData.model_exists ? "var(--up)" : "var(--down)"],
          ["Trained at",  mlData.trained_at ? mlData.trained_at.slice(0,16).replace("T"," ") : "—", "var(--text)"],
          ["N signals",   mlData.n_signals ?? "—", "var(--text)"],
          ["OOS WR",      mlData.oos_win_rate != null ? `${mlData.oos_win_rate.toFixed(1)}%` : "—", "var(--accent)"],
          ["OOS P/F",     mlData.oos_profit_factor != null ? `${mlData.oos_profit_factor.toFixed(2)}×` : "—", "var(--accent)"],
        ].map(([label, val, color]) => (
          <div key={label} style={{ background:"var(--bg-1)", border:"1px solid var(--line)", borderRadius:8, padding:"10px 14px", minWidth:110 }}>
            <div style={{ fontSize:9, fontFamily:"var(--font-mono)", color:"var(--text-faint)", textTransform:"uppercase", letterSpacing:"0.1em", marginBottom:4 }}>{label}</div>
            <div style={{ fontSize:15, fontWeight:700, color }}>{val}</div>
          </div>
        ))}
        <button className="btn primary" onClick={triggerTrain} disabled={training}
          style={{ fontSize:11, padding:"10px 16px", alignSelf:"flex-end" }}>
          {training ? "Training…" : "Retrain"}
        </button>
      </div>
      {trainMsg && <div style={{ fontSize:11, color: trainMsg.includes("fail") ? "var(--down)" : "var(--up)", marginBottom:12, fontFamily:"var(--font-mono)" }}>{trainMsg}</div>}

      {/* ── Feature importances ── */}
      {fi.length > 0 ? (
        <div>
          <div style={{ fontSize:11, fontFamily:"var(--font-mono)", color:"var(--text-faint)", textTransform:"uppercase", letterSpacing:"0.1em", marginBottom:12 }}>
            Feature Importances (XGBoost gain)
          </div>
          {fi.slice(0, 20).map((f, i) => (
            <div key={f.feature} style={{ display:"flex", alignItems:"center", gap:8, marginBottom:6 }}>
              <div style={{ fontSize:11, fontFamily:"var(--font-mono)", color:"var(--text-faint)", width:14, textAlign:"right" }}>{i+1}</div>
              <div style={{ fontSize:11, fontFamily:"var(--font-mono)", color:"var(--text)", width:180, overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}
                title={f.feature}>{f.feature}</div>
              <div style={{ flex:1, height:8, background:"var(--bg-2)", borderRadius:4, overflow:"hidden" }}>
                <div style={{ height:"100%", width:`${((f.importance || 0) / maxImp) * 100}%`,
                  background: i < 5 ? "var(--accent)" : i < 10 ? "rgba(16,185,129,0.5)" : "var(--bg-card)",
                  borderRadius:4, transition:"width 0.3s" }}/>
              </div>
              <div style={{ fontSize:10, fontFamily:"var(--font-mono)", color:"var(--text-faint)", width:50, textAlign:"right" }}>
                {(f.importance || 0).toFixed(4)}
              </div>
            </div>
          ))}
          <div style={{ fontSize:10, color:"var(--text-faint)", fontFamily:"var(--font-mono)", marginTop:8 }}>
            Top-20 of {fi.length} features · Green = top 5 · Dim = lower importance
          </div>
        </div>
      ) : (
        <EmptyBt msg={mlData.model_exists ? "Feature importances not recorded — retrain to generate." : "No model trained yet. Click Retrain after ≥50 resolved signals are available."}/>
      )}
    </div>
  );
}

/* ─── Shared table helpers ───────────────────────────────────────────────────── */
function SortableTable({ title, cols, rows, colors = [], defaultSort = null }) {
  const [sortCol, setSortCol] = useState(defaultSort?.col ?? null);
  const [sortDir, setSortDir] = useState(defaultSort?.dir ?? "desc");

  const toggleSort = (ci) => {
    if (sortCol === ci) setSortDir(d => d === "asc" ? "desc" : "asc");
    else { setSortCol(ci); setSortDir("desc"); }
  };

  const sortedRows = useMemo(() => {
    if (sortCol === null) return rows;
    return [...rows].sort((a, b) => {
      const av = a[sortCol], bv = b[sortCol];
      const toNum = v => {
        if (v == null || v === "—") return sortDir === "asc" ? Infinity : -Infinity;
        if (typeof v === "number") return v;
        if (typeof v === "string") {
          const n = parseFloat(v.replace(/[^0-9.+-]/g, ""));
          return isNaN(n) ? (sortDir === "asc" ? Infinity : -Infinity) : n;
        }
        return 0;
      };
      const an = toNum(av), bn = toNum(bv);
      return sortDir === "asc" ? an - bn : bn - an;
    });
  }, [rows, sortCol, sortDir]);

  const isLeft = ci => ci === 0;
  return (
    <div>
      {title && <div style={{ fontSize:11, fontWeight:600, color:"var(--text-dim)", textTransform:"uppercase", letterSpacing:"0.08em", marginBottom:10 }}>{title}</div>}
      <table style={{ width:"100%", borderCollapse:"collapse", fontSize:12, fontFamily:"var(--font-mono)" }}>
        <thead>
          <tr style={{ borderBottom:"1px solid var(--line)", color:"var(--text-faint)", fontSize:10, textTransform:"uppercase" }}>
            {cols.map((h, ci) => (
              <th key={ci} onClick={() => toggleSort(ci)}
                style={{ padding:"7px 10px", textAlign: isLeft(ci) ? "left" : "right", fontWeight:500,
                  cursor:"pointer", userSelect:"none", whiteSpace:"nowrap",
                  color: sortCol === ci ? "var(--accent)" : undefined }}>
                {h}
                {sortCol === ci
                  ? <span style={{ marginLeft:4, fontSize:9 }}>{sortDir === "asc" ? "▲" : "▼"}</span>
                  : <span style={{ marginLeft:4, fontSize:9, opacity:0.3 }}>⇅</span>}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sortedRows.map((row, ri) => (
            <tr key={ri} style={{ borderBottom:"1px solid var(--line)" }}>
              {row.map((cell, ci) => {
                const colorFn = colors[ci];
                const color = typeof colorFn === "function" ? colorFn(cell, ri) : (typeof colorFn === "string" ? colorFn : undefined);
                return <td key={ci} style={{ padding:"7px 10px", textAlign: isLeft(ci) ? "left" : "right", color, fontWeight: ci===0 ? 600 : 400 }}>{cell}</td>;
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function BtTable({ title, cols, rows, colors = [] }) {
  return <SortableTable title={title} cols={cols} rows={rows} colors={colors}/>;
}
function EmptyBt({ msg }) {
  return <div style={{ padding:"40px 0", textAlign:"center", color:"var(--text-faint)", fontSize:12 }}>{msg}</div>;
}

function CalibrationChart({ data }) {
  if (!data || data.length === 0) return null;
  const W = 480, H = 300, PAD = 40;
  const plotW = W - PAD * 2, plotH = H - PAD * 2;
  const xPct = v => PAD + (v / 100) * plotW;
  const yPct = v => H - PAD - (v / 100) * plotH;
  const diag = `M${xPct(40)} ${yPct(40)} L${xPct(100)} ${yPct(100)}`;

  return (
    <div style={{ overflowX:"auto" }}>
      <svg aria-hidden="true" width={W} height={H} style={{ background:"var(--bg-2)", borderRadius:8, border:"1px solid var(--line)", display:"block" }}>
        {[40,50,60,70,80,90,100].map(v => (
          <g key={v}>
            <line x1={PAD} y1={yPct(v)} x2={W-PAD} y2={yPct(v)} stroke="var(--line)" strokeWidth={0.5}/>
            <line x1={xPct(v)} y1={PAD} x2={xPct(v)} y2={H-PAD} stroke="var(--line)" strokeWidth={0.5}/>
            <text x={PAD - 6} y={yPct(v) + 4} fontSize={9} fill="var(--text-faint)" textAnchor="end">{v}%</text>
            <text x={xPct(v)} y={H - PAD + 14} fontSize={9} fill="var(--text-faint)" textAnchor="middle">{v}%</text>
          </g>
        ))}
        <text x={W/2} y={H - 4} fontSize={10} fill="var(--text-dim)" textAnchor="middle">Predicted Confidence</text>
        <text x={12} y={H/2} fontSize={10} fill="var(--text-dim)" textAnchor="middle" transform={`rotate(-90 12 ${H/2})`}>Actual Win Rate</text>
        <path d={diag} stroke="var(--text-faint)" strokeWidth={1} strokeDasharray="4 3" fill="none"/>
        <text x={xPct(92)} y={yPct(94)} fontSize={9} fill="var(--text-faint)">Perfect</text>
        {data.map((pt, i) => {
          const x = xPct(pt.predicted);
          const yPred = yPct(pt.predicted);
          const yActual = yPct(pt.actual);
          const overconf = pt.actual < pt.predicted;
          return (
            <line key={i} x1={x} y1={yPred} x2={x} y2={yActual}
              stroke={overconf ? "var(--down)" : "var(--up)"} strokeWidth={10} strokeLinecap="round" opacity={0.4}/>
          );
        })}
        {data.map((pt, i) => (
          <g key={i}>
            <circle cx={xPct(pt.predicted)} cy={yPct(pt.actual)} r={5}
              fill={pt.actual >= pt.predicted ? "var(--up)" : "var(--down)"}
              stroke="var(--bg-1)" strokeWidth={1.5}/>
            <title>{pt.bucket}: predicted {pt.predicted}% · actual {pt.actual}% · n={pt.count}</title>
          </g>
        ))}
        {data.map((pt, i) => (
          <text key={i} x={xPct(pt.predicted)} y={yPct(pt.actual) - 9}
            fontSize={9} fill="var(--text-faint)" textAnchor="middle">n={pt.count}</text>
        ))}
      </svg>
      <div style={{ display:"flex", gap:16, marginTop:10, fontSize:11, color:"var(--text-faint)", fontFamily:"var(--font-mono)" }}>
        <span style={{ display:"flex", alignItems:"center", gap:4 }}>
          <span style={{ width:10, height:10, borderRadius:"50%", background:"var(--up)", display:"inline-block" }}/>
          Underconfident (model is more cautious than needed)
        </span>
        <span style={{ display:"flex", alignItems:"center", gap:4 }}>
          <span style={{ width:10, height:10, borderRadius:"50%", background:"var(--down)", display:"inline-block" }}/>
          Overconfident (model overstates certainty)
        </span>
      </div>
    </div>
  );
}
