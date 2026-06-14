/* ─── Signal row ────────────────────────────────────────────────────────────── */
function SignalRow({ s, active, expanded, onToggle, onOpen, onFullDetail, onSend, onSkip,
                    suppressed, outcomeByTicker, tickerHistory, allSignals }) {
  const up = (s.change || 0) >= 0;
  const conf = s.confidence || 0;

  // Mini confidence sparkline from same-ticker-same-action signals already in feed.
  // No extra API call — derives from the allSignals array already in memory.
  const miniConf = useMemo(() => {
    if (!allSignals) return null;
    const prev = (allSignals || [])
      .filter(x => x.ticker === s.ticker && x.action === s.action && x.id !== s.id)
      .sort((a, b) => (a.ts || "").localeCompare(b.ts || ""))
      .slice(-4)
      .map(x => x.confidence || 0);
    return prev.length >= 1 ? [...prev, conf] : null;
  }, [allSignals, s.ticker, s.action, s.id, conf]);
  return (
    <div className={`signal${active?" active":""}${expanded?" expanded":""}${suppressed?" suppressed":""}`}>
      <button className="signal-row-inner" onClick={onToggle} aria-expanded={expanded} aria-label={`${s.action} ${s.ticker} signal`}>
        <div className={`signal-dot ${s.action}`}/>
        <div className="signal-body">
          <div className="signal-top">
            <span className={`signal-verb ${s.action}`}>{s.action}</span>
            <span className="signal-ticker">{s.ticker}</span>
            {s.style && <span className={`style-badge ${s.style}`}>{s.style}</span>}
            {s.daysToEarnings != null && s.daysToEarnings <= 5 && s.daysToEarnings >= 0 && (
              <span title={`Earnings in ${s.daysToEarnings}d${s.nextEarningsDate ? ` (${s.nextEarningsDate})` : ""}`}
                style={{ fontSize:9, fontFamily:"var(--font-mono)", fontWeight:700,
                  color:"var(--warn)", background:"var(--warn-soft)",
                  border:"1px solid color-mix(in oklch, var(--warn) 35%, transparent)", borderRadius:3,
                  padding:"1px 4px", whiteSpace:"nowrap", letterSpacing:"0.04em" }}>
                ⚠ {s.daysToEarnings}d ERN
              </span>
            )}
            {s.expiresAt && (() => {
              const minsLeft = Math.round((new Date(s.expiresAt) - Date.now()) / 60000);
              if (minsLeft > 0 && minsLeft <= 1440) {
                const label = minsLeft < 60 ? `${minsLeft}m` : `${Math.round(minsLeft / 60)}h`;
                return (
                  <span title={`Signal expires at ${s.expiresAt}`}
                    style={{ fontSize:9, fontFamily:"var(--font-mono)", fontWeight:700,
                      color:"var(--down)", background:"color-mix(in oklch, var(--down) 10%, transparent)",
                      border:"1px solid color-mix(in oklch, var(--down) 30%, transparent)", borderRadius:3,
                      padding:"1px 4px", whiteSpace:"nowrap", letterSpacing:"0.04em" }}>
                    ⏱ {label}
                  </span>
                );
              }
              return null;
            })()}
            {s.session && s.session !== "regular" && s.session !== "closed" && (
              <span title={s.session === "pre" ? "Generated during pre-market session" : "Generated after market close"}
                style={{ fontSize:9, fontFamily:"var(--font-mono)", fontWeight:700,
                  color: s.session === "pre" ? "var(--accent)" : "var(--text-dim)",
                  background: s.session === "pre" ? "var(--accent-soft)" : "rgba(100,100,100,0.12)",
                  border: `1px solid ${s.session === "pre" ? "color-mix(in oklch, var(--accent) 30%, transparent)" : "rgba(100,100,100,0.25)"}`,
                  borderRadius:3, padding:"1px 4px", whiteSpace:"nowrap", letterSpacing:"0.06em" }}>
                {s.session === "pre" ? "PRE" : "AH"}
              </span>
            )}
            <span className="action-subtitle">· {ACTION_SUBTITLE[s.action]}</span>
          </div>
          <div className="signal-head">{s.headline}</div>
          {/* Entry / Stop / Target chips — visible without expanding */}
          {s.entry && !suppressed && (
            <div style={{ display:"flex", gap:5, marginTop:3, flexWrap:"wrap" }}>
              <span style={{ fontFamily:"var(--font-mono)", fontSize:9, color:"var(--text-faint)",
                padding:"1px 5px", background:"var(--bg-3)", borderRadius:3, letterSpacing:"0.04em" }}>
                E <strong style={{ color:"var(--text)" }}>${fmt(s.entry)}</strong>
              </span>
              {s.stop && <span style={{ fontFamily:"var(--font-mono)", fontSize:9,
                padding:"1px 5px", background:"color-mix(in oklch, var(--down) 10%, transparent)", borderRadius:3,
                color:"var(--down)", letterSpacing:"0.04em" }}>
                S ${fmt(s.stop)}
              </span>}
              {s.target && <span style={{ fontFamily:"var(--font-mono)", fontSize:9,
                padding:"1px 5px", background:"color-mix(in oklch, var(--up) 10%, transparent)", borderRadius:3,
                color:"var(--up)", letterSpacing:"0.04em" }}>
                T ${fmt(s.target)}
              </span>}
            </div>
          )}
        </div>
        <div className="signal-right">
          <div style={{ display:"flex", flexDirection:"column", alignItems:"flex-end", gap:2 }}>
            <span className="mono" style={{ fontSize:11 }}>{conf.toFixed(0)}%</span>
            <div title={`Confidence: ${conf.toFixed(0)}%`}
              style={{ width:42, height:4, borderRadius:2, background:"var(--bg-3)", overflow:"hidden" }}>
              <div style={{
                height:"100%", borderRadius:2,
                width:`${conf}%`,
                background: conf >= 75 ? "var(--up)"
                          : conf >= 62 ? "var(--accent)"
                          : conf >= 50 ? "var(--warn)"
                          : "var(--down)",
                transition:"width 0.3s",
              }}/>
            </div>
          </div>
          {s.confidence_warning && (
            <span
              title="Confidence Divergence: signal confidence significantly exceeds its historical win rate. Review conflicting signals before acting."
              style={{ fontSize:9, fontWeight:700, color:"var(--warn)", fontFamily:"var(--font-mono)",
                       letterSpacing:"0.04em", background:"var(--warn-soft)",
                       padding:"1px 4px", borderRadius:3,
                       border:"1px solid color-mix(in oklch, var(--warn) 40%, transparent)", marginLeft:2,
                       whiteSpace:"nowrap" }}>⚠ CALIB</span>
          )}
          {/* Mini confidence sparkline — 5-point trend from same-ticker signals in memory */}
          {miniConf && miniConf.length >= 2 && (() => {
            const lo = Math.min(...miniConf), hi = Math.max(...miniConf, lo + 1);
            const W = 28, H = 14;
            const xs = i => (i / (miniConf.length - 1)) * W;
            const ys = v => H - ((v - lo) / (hi - lo)) * H;
            const d = miniConf.map((v,i) => `${i===0?"M":"L"}${xs(i).toFixed(1)} ${ys(v).toFixed(1)}`).join(" ");
            const rising = miniConf[miniConf.length-1] >= miniConf[0];
            return (
              <svg aria-hidden="true" viewBox={`0 0 ${W} ${H}`} style={{ width:W, height:H, flexShrink:0 }}
                title={`Confidence trend: ${miniConf.map(c=>c.toFixed(0)).join(" → ")}%`}>
                <path d={d} stroke={rising?"var(--up)":"var(--down)"} strokeWidth="1.2" fill="none" strokeLinecap="round"/>
              </svg>
            );
          })()}
          <span className="mono faint" title={fmtETFull(s.ts)}>
            {fmtETTime(s.ts).replace(" ET", "")}
          </span>
          <span className="chev">
            <svg aria-hidden="true" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
          </span>
        </div>
      </button>

      {expanded && (
        <div className="signal-expand" onClick={e => e.stopPropagation()}>
          <div className="se-row">
            <div>
              <div className="se-price mono">${fmt(s.price)}</div>
              <div className={`se-change mono ${up?"up":"down"}`}>{sgn(s.change||0)}{fmt(s.change||0)} ({sgn(s.changePct||0)}{fmt(s.changePct||0)}%) today</div>
            </div>
            <div style={{ textAlign:"right" }}>
              <div className="mono" style={{ fontSize:10, color:"var(--text-faint)", textTransform:"uppercase", letterSpacing:"0.1em" }}>
                <Tip term="CONFIDENCE">Confidence</Tip>
              </div>
              <div className="mono" style={{ fontSize:15, color:"var(--accent)", fontWeight:600 }}>{conf.toFixed(0)}%</div>
            </div>
          </div>
          <div className="se-head"><strong style={{ color:"var(--text)" }}>{ACTION_SUBTITLE[s.action]}.</strong> {s.headline}</div>
          {s.entry && (
            <div className="se-stats">
              <div className="se-stat"><div className="l"><Tip term="R:R">R:R</Tip></div><div className="v">{s.rr}</div></div>
              <div className="se-stat"><div className="l"><Tip term="ENTRY">Entry</Tip></div><div className="v">${fmt(s.entry)}</div></div>
              <div className="se-stat"><div className="l"><Tip term="STOP">Stop</Tip></div><div className="v down">${fmt(s.stop)}</div></div>
              <div className="se-stat"><div className="l"><Tip term="TARGET">Target</Tip></div><div className="v up">${fmt(s.target)}</div></div>
            </div>
          )}
          <div style={{ display:"flex", alignItems:"center", gap:8, padding:"4px 0 2px" }}>
            <span style={{ fontSize:9, color:"var(--text-faint)", fontFamily:"var(--font-mono)", textTransform:"uppercase", letterSpacing:"0.08em" }}>Conf trend</span>
            <ConfidenceTrend ticker={s.ticker} current={s.confidence || 65}/>
          </div>
          <div className="se-actions">
            <button className="se-btn primary" onClick={() => { onOpen(); onFullDetail?.(); }}>Full detail →</button>
            <button className="se-btn" onClick={onSend}><Icon name="telegram" size={11}/> Telegram</button>
            <button className="se-btn" onClick={onSkip}><Icon name="clock" size={11}/> Skip</button>
            <OutcomeStrip ticker={s.ticker} outcomeByTicker={outcomeByTicker} history={tickerHistory}/>
          </div>
        </div>
      )}
    </div>
  );
}

/* ─── Telegram / Delivery pane ──────────────────────────────────────────────── */
function TelegramPane({ log, online, onOpenAccount, onClose }) {
  const [view, setView] = useState("log");
  const sent    = (log||[]).filter(l => l.status === "sent");
  const failed  = (log||[]).filter(l => l.status === "fail");
  const today   = (log||[]).filter(l => {
    if (!l.created_at) return false;
    return new Date(l.created_at).toDateString() === new Date().toDateString();
  });

  return (
    <div className="pane">
      <div className="pane-head">
        <span className="title">Delivery</span>
        <span className="sep"/>
        <span className={`chip ${online?"accent":""}`}>
          <span style={{ width:6, height:6, borderRadius:"50%", background:"currentColor" }}/>
          {online ? "Live" : "Offline"}
        </span>
        <div className="right">
          <span className="chip">{today.length} today</span>
          {onClose && (
            <button className="btn ghost" onClick={onClose} style={{ marginLeft: 8 }}>
              <Icon name="x" size={14}/> Close
            </button>
          )}
        </div>
      </div>
      <div className="del-tabs">
        <div className={`del-tab ${view==="log"?"active":""}`} onClick={() => setView("log")} role="button" tabIndex={0}>Send log</div>
        <div className={`del-tab ${view==="info"?"active":""}`} onClick={() => setView("info")} role="button" tabIndex={0}>Setup</div>
      </div>

      {view === "log" ? (
        <div className="del-log active">
          <div style={{ fontFamily:"var(--font-mono)", fontSize:10, color:"var(--text-faint)", textTransform:"uppercase", letterSpacing:"0.1em", paddingBottom:10, borderBottom:"1px solid var(--line)", marginBottom:4 }}>
            {sent.length} sent · {failed.length} failed
          </div>
          {(log||[]).slice(0, 80).map((l, i) => (
            <div key={i} className="log-row">
              <span className="log-time">{(l.time||"").slice(0,8)}</span>
              <span className={`log-status ${l.status}`}>{l.status}</span>
              <span className="log-msg">{l.message}</span>
            </div>
          ))}
          {(log||[]).length === 0 && (
            <div style={{ padding:"40px 0", textAlign:"center", color:"var(--text-faint)", fontSize:12 }}>
              No signals sent yet today.
            </div>
          )}
        </div>
      ) : (
        <div style={{ padding:"16px 16px", fontSize:13, color:"var(--text-dim)", lineHeight:1.7 }}>
          <div style={{ marginBottom:16 }}>
            <div style={{ fontSize:11, fontFamily:"var(--font-mono)", textTransform:"uppercase", letterSpacing:"0.1em", color:"var(--text-faint)", marginBottom:6 }}>Telegram bot</div>
            <div>Send <code style={{ background:"var(--bg-2)", padding:"1px 6px", borderRadius:4, fontSize:11 }}>/start &lt;code&gt;</code> to your Signal.Trade bot after linking in Account Settings.</div>
          </div>
          <div style={{ marginBottom:16 }}>
            <div style={{ fontSize:11, fontFamily:"var(--font-mono)", textTransform:"uppercase", letterSpacing:"0.1em", color:"var(--text-faint)", marginBottom:6 }}>Delivery rules</div>
            <ul style={{ paddingLeft:16, color:"var(--text-dim)", fontSize:12 }}>
              <li>Confidence above threshold</li>
              <li>Minimum 2% profit potential</li>
              <li>Market hours only (10:00–15:30 ET)</li>
              <li>24-hour cooldown per ticker+action</li>
            </ul>
          </div>
          <a href="#" onClick={e => { e.preventDefault(); onOpenAccount?.(); }}
            style={{ fontSize:12, color:"var(--accent)", cursor:"pointer" }} role="button" tabIndex={0}>
            Open Account Settings →
          </a>
        </div>
      )}
    </div>
  );
}

/* ─── NoteEditor ─────────────────────────────────────────────────────────────── */
function NoteEditor({ signal, onSave }) {
  const [note, setNote] = useState(signal?.notes || "");
  const [saved, setSaved] = useState(false);
  useEffect(() => { setNote(signal?.notes || ""); setSaved(false); }, [signal?.id]);
  const handleSave = () => {
    onSave(signal.id, note);
    setSaved(true);
    setTimeout(() => setSaved(false), 1800);
  };
  return (
    <div style={{ margin:"0 20px 0", padding:"10px 12px", background:"var(--bg-2)", border:"1px solid var(--line)", borderRadius:6 }}>
      <div style={{ fontSize:9, fontFamily:"var(--font-mono)", textTransform:"uppercase", letterSpacing:"0.1em", color:"var(--text-faint)", marginBottom:6 }}>
        Trade journal note
      </div>
      <textarea
        value={note}
        onChange={e => { setNote(e.target.value); setSaved(false); }}
        placeholder="Add your notes, thesis, or trade rationale…"
        rows={2}
        style={{ width:"100%", background:"var(--bg)", border:"1px solid var(--line)", borderRadius:4, color:"var(--text)", fontFamily:"var(--font-sans)", fontSize:12, padding:"6px 8px", resize:"vertical", outline:"none", lineHeight:1.5 }}
      />
      <div style={{ display:"flex", justifyContent:"flex-end", marginTop:4 }}>
        <button className="btn" style={{ fontSize:11, padding:"4px 12px", color: saved ? "var(--up)" : undefined }} onClick={handleSave}>
          {saved ? "✓ Saved" : "Save note"}
        </button>
      </div>
    </div>
  );
}

/* ─── FilterChips ────────────────────────────────────────────────────────────── */
function FilterChips({ filter, setFilter, counts }) {
  const chips = [
    { id: "all",   label: "All",         count: counts.all },
    { id: "buy",   label: "BUY only",    count: counts.buy,  dot: "var(--up)" },
    { id: "sell",  label: "SELL only",   count: counts.sell, dot: "var(--down)" },
    { id: "high",  label: "High conf 75%+", count: counts.high, accent: true },
    { id: "today", label: "Today",       count: counts.today },
  ];
  return (
    <div className="filter-chips">
      {chips.map(c => (
        <button key={c.id} className={`fc ${filter === c.id ? "on" : ""} ${c.accent ? "accent" : ""}`} onClick={() => setFilter(c.id)}>
          {c.dot && <span className="fc-dot" style={{ background: c.dot }}/>}
          <span>{c.label}</span>
          <span className="fc-count mono">{c.count}</span>
        </button>
      ))}
      <div style={{ flex:1 }}/>
      <div className="saved-views">
        <span className="sv-label mono">VIEW</span>
        <button className="sv-btn">Morning scan ▾</button>
      </div>
    </div>
  );
}
