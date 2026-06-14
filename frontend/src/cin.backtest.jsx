/* global React */
// SIGNAL.TRADE cinematic — Backtest Lab.
// Fetches real /api/signals/backtest, /api/signals/backtest/horizons and
// /api/signals/track-record, while keeping the toy equity-curve simulator.
const { useState: bUseState, useEffect: bUseEffect, useMemo: bUseMemo } = React;

function EquityChart({ result, compare }) {
  const w = 760, h = 300;
  const all = compare ? [...result.curve, ...compare.curve] : result.curve;
  const min = Math.min(...all), max = Math.max(...all);
  const rng = max - min || 1;
  const toPts = (curve) => curve.map((v, i) => [(i / (curve.length - 1)) * w, h - 18 - ((v - min) / rng) * (h - 44)]);
  const pts = toPts(result.curve);
  const d = pts.map((p, i) => `${i ? "L" : "M"}${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(" ");
  // drawdown shading: running max line vs curve
  let peak = result.curve[0];
  const peakPts = result.curve.map((v, i) => { if (v > peak) peak = v; return [(i / (result.curve.length - 1)) * w, h - 18 - ((peak - min) / rng) * (h - 44)]; });
  const ddPath = peakPts.map((p, i) => `${i ? "L" : "M"}${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(" ")
    + " " + [...pts].reverse().map((p) => `L${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(" ") + " Z";
  let cmpD = null;
  if (compare) {
    const cp = toPts(compare.curve);
    cmpD = cp.map((p, i) => `${i ? "L" : "M"}${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(" ");
  }
  const gridY = [0.25, 0.5, 0.75].map((f) => 18 + (h - 44) * f);
  return (
    <svg viewBox={`0 0 ${w} ${h}`} style={{ width: "100%", height: "auto", display: "block" }}>
      <defs>
        <linearGradient id="eqfill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#22d3ee" stopOpacity="0.16"></stop>
          <stop offset="100%" stopColor="#22d3ee" stopOpacity="0"></stop>
        </linearGradient>
      </defs>
      {gridY.map((y, i) => (
        <g key={i}>
          <line x1="0" x2={w} y1={y} y2={y} stroke="rgba(255,255,255,0.045)" strokeDasharray="2 5"></line>
          <text x={w - 4} y={y - 5} textAnchor="end" fontSize="9.5" fill="var(--text-faint)" fontFamily="var(--font-mono)">
            ${Math.round((max - rng * ((y - 18) / (h - 44))) / 1000)}k
          </text>
        </g>
      ))}
      {/* drawdown shading between running peak and equity */}
      <path d={ddPath} fill="rgba(251,77,109,0.10)"></path>
      <path d={`${d} L${w},${h} L0,${h} Z`} fill="url(#eqfill)"></path>
      <path d={d} fill="none" stroke="var(--bull)" strokeWidth="1.8" strokeLinejoin="round"></path>
      {cmpD && <path d={cmpD} fill="none" stroke="var(--neutral)" strokeWidth="1.5" strokeDasharray="5 4" strokeLinejoin="round" opacity="0.9"></path>}
    </svg>
  );
}

function ParamSlider({ label, value, min, max, step, unit, onChange }) {
  return (
    <div style={{ marginBottom: 18 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 8 }}>
        <span style={{ fontSize: 12.5, color: "var(--text-dim)", fontWeight: 500 }}>{label}</span>
        <span className="mono" style={{ fontSize: 12.5, color: "var(--bull)", fontWeight: 600 }}>{value}{unit}</span>
      </div>
      <input type="range" min={min} max={max} step={step} value={value} onChange={(e) => onChange(Number(e.target.value))}></input>
    </div>
  );
}

function SourceToggle({ label, on, onChange }) {
  return (
    <button onClick={() => onChange(!on)} style={{
      display: "flex", alignItems: "center", justifyContent: "space-between", gap: 10,
      width: "100%", padding: "9px 0", background: "none", border: "none",
      borderBottom: "1px solid var(--line-soft)", color: on ? "var(--text)" : "var(--text-faint)",
      fontSize: 12.5, fontWeight: 500, transition: "color 0.2s var(--ease)",
    }}>
      {label}
      <span className={`tgl ${on ? "on" : ""}`}></span>
    </button>
  );
}

function MetricCard({ label, value, dp, suffix, good }) {
  return (
    <div className="glass glass-hover" style={{ padding: "16px 18px" }}>
      <div className="kicker" style={{ marginBottom: 8 }}>{label}</div>
      <div style={{ fontSize: 24, fontWeight: 700 }}>
        <span style={{ color: good ? "var(--bull)" : "var(--bear)" }}>
          <Num value={value} dp={dp} suffix={suffix}></Num>
        </span>
      </div>
    </div>
  );
}

function RealMetricCard({ label, value, sub, good }) {
  return (
    <div className="glass glass-hover" style={{ padding: "16px 18px" }}>
      <div className="kicker" style={{ marginBottom: 8 }}>{label}</div>
      <div className="mono" style={{ fontSize: 24, fontWeight: 700, color: good ? "var(--bull)" : "var(--bear)" }}>{value}</div>
      {sub && <div style={{ fontSize: 10.5, color: "var(--text-faint)", marginTop: 4 }}>{sub}</div>}
    </div>
  );
}

function HorizonMetric({ label, value, color }) {
  return (
    <div style={{ minWidth: 0 }}>
      <div className="kicker" style={{ marginBottom: 3 }}>{label}</div>
      <div className="mono" style={{ fontSize: 15, fontWeight: 700, color: color || "var(--text)", whiteSpace: "nowrap" }}>{value}</div>
    </div>
  );
}

function HorizonCard({ h }) {
  const has = h.n > 0 && h.win_rate != null;
  return (
    <div className="glass" style={{ padding: "14px 16px" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
        <span className="mono" style={{ fontSize: 13, fontWeight: 700 }}>{h.horizon}</span>
        <span className="kicker" style={{ marginLeft: "auto" }}>{h.n} signals</span>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px 12px" }}>
        <HorizonMetric label="Win rate" value={has ? `${h.win_rate.toFixed(1)}%` : "—"} color={has && h.win_rate > 50 ? "var(--bull)" : "var(--text)"}></HorizonMetric>
        <HorizonMetric label="Avg return" value={h.avg_return != null ? `${h.avg_return >= 0 ? "+" : ""}${h.avg_return.toFixed(2)}%` : "—"} color={h.avg_return >= 0 ? "var(--bull)" : "var(--bear)"}></HorizonMetric>
        <HorizonMetric label="Sharpe" value={h.sharpe != null ? h.sharpe.toFixed(2) : "—"} color={h.sharpe > 1 ? "var(--bull)" : "var(--text)"}></HorizonMetric>
        <HorizonMetric label="Avg win" value={h.avg_win != null ? `+${h.avg_win.toFixed(2)}%` : "—"} color="var(--bull)"></HorizonMetric>
      </div>
    </div>
  );
}

function TrackTable({ rows }) {
  if (!Array.isArray(rows) || !rows.length) return null;
  return (
    <div className="glass" style={{ padding: "18px 20px", marginTop: 14 }}>
      <div className="kicker" style={{ marginBottom: 12 }}>PER-TICKER TRACK RECORD</div>
      <div style={{ overflowX: "auto" }}>
        <table className="mono" style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
          <thead>
            <tr style={{ textAlign: "right", color: "var(--text-faint)" }}>
              <th style={{ textAlign: "left", padding: "6px 8px", fontWeight: 500 }}>Ticker</th>
              <th style={{ padding: "6px 8px", fontWeight: 500 }}>Signals</th>
              <th style={{ padding: "6px 8px", fontWeight: 500 }}>Win %</th>
              <th style={{ padding: "6px 8px", fontWeight: 500 }}>Avg ret</th>
              <th style={{ padding: "6px 8px", fontWeight: 500 }}>Sharpe</th>
              <th style={{ padding: "6px 8px", fontWeight: 500 }}>Best</th>
              <th style={{ padding: "6px 8px", fontWeight: 500 }}>Worst</th>
            </tr>
          </thead>
          <tbody>
            {rows.slice(0, 12).map((r, i) => (
              <tr key={i} style={{ borderTop: "1px solid var(--line-soft)", textAlign: "right" }}>
                <td style={{ textAlign: "left", padding: "8px", fontWeight: 700 }}>{r.ticker}</td>
                <td style={{ padding: "8px", color: "var(--text-dim)" }}>{r.signals}</td>
                <td style={{ padding: "8px", color: r.win_rate >= 60 ? "var(--bull)" : "var(--text)" }}>{r.win_rate.toFixed(1)}%</td>
                <td style={{ padding: "8px", color: r.avg_return >= 0 ? "var(--bull)" : "var(--bear)" }}>{r.avg_return >= 0 ? "+" : ""}{r.avg_return.toFixed(2)}%</td>
                <td style={{ padding: "8px" }}>{r.sharpe != null ? r.sharpe.toFixed(2) : "—"}</td>
                <td style={{ padding: "8px", color: "var(--bull)" }}>+{r.best.toFixed(2)}%</td>
                <td style={{ padding: "8px", color: "var(--bear)" }}>{r.worst.toFixed(2)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

const BT_PRESET_B = { confMin: 55, holdDays: 3, stopPct: 8, sources: { tech: true, flow: false, options: true, macro: false } };

function PageBacktest() {
  const [confMin, setConfMin] = bUseState(70);
  const [holdDays, setHoldDays] = bUseState(7);
  const [stopPct, setStopPct] = bUseState(5);
  const [sources, setSources] = bUseState({ tech: true, flow: true, options: true, macro: true });
  const [compare, setCompare] = bUseState(false);

  const [btSummary, setBtSummary] = bUseState(null);
  const [horizons, setHorizons] = bUseState([]);
  const [trackRecord, setTrackRecord] = bUseState([]);
  const [btLoading, setBtLoading] = bUseState(true);

  bUseEffect(() => {
    let alive = true;
    setBtLoading(true);
    Promise.all([
      apiFetch("/api/signals/backtest"),
      apiFetch("/api/signals/backtest/horizons"),
      apiFetch("/api/signals/track-record"),
    ]).then(([sum, hrs, trk]) => {
      if (!alive) return;
      if (sum && typeof sum === "object") setBtSummary(sum);
      if (Array.isArray(hrs)) setHorizons(hrs);
      if (Array.isArray(trk)) setTrackRecord(trk);
    }).catch(() => {}).finally(() => { if (alive) setBtLoading(false); });
    return () => { alive = false; };
  }, []);

  const result = bUseMemo(() => runBacktest({ confMin, holdDays, stopPct, sources }), [confMin, holdDays, stopPct, sources]);
  const cmpResult = bUseMemo(() => (compare ? runBacktest(BT_PRESET_B) : null), [compare]);
  const m = result.metrics;
  const cm = cmpResult ? cmpResult.metrics : null;
  const setSource = (k, v) => setSources((s) => ({ ...s, [k]: v }));

  const realCards = btSummary && btSummary.resolved > 0 ? (
    <div className="glass" style={{ padding: "18px 20px", marginBottom: 14 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12, flexWrap: "wrap" }}>
        <span className="kicker">LIVE BACKTEST · {btSummary.resolved} RESOLVED SIGNALS</span>
        <span className="kicker" style={{ marginLeft: "auto", color: "var(--text-faint)" }}>Primary horizon {btSummary.primary_horizon || "7d"}</span>
      </div>
      <div className="bt-metrics" style={{ marginBottom: 14 }}>
        <RealMetricCard label="WIN RATE" value={`${btSummary.win_rate.toFixed(1)}%`} good={btSummary.win_rate > 50}></RealMetricCard>
        <RealMetricCard label="AVG RETURN" value={`${btSummary.avg_return >= 0 ? "+" : ""}${btSummary.avg_return.toFixed(2)}%`} good={btSummary.avg_return > 0}></RealMetricCard>
        <RealMetricCard label="SHARPE" value={btSummary.sharpe != null ? btSummary.sharpe.toFixed(2) : "—"} good={btSummary.sharpe > 1}></RealMetricCard>
        <RealMetricCard label="MAX DD" value={btSummary.max_drawdown != null ? `${btSummary.max_drawdown.toFixed(1)}%` : "—"} good={btSummary.max_drawdown > -10}></RealMetricCard>
      </div>
      <div className="kicker" style={{ marginBottom: 10 }}>BY HORIZON</div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 10 }}>
        {horizons.map((h) => <HorizonCard key={h.horizon} h={h}></HorizonCard>)}
      </div>
    </div>
  ) : null;

  return (
    <div className="page wrap" style={{ paddingTop: 24, paddingBottom: 56 }}>
      <div className="bt-grid">
        {/* Parameter builder */}
        <aside className="glass" style={{ padding: 20, alignSelf: "start" }}>
          <div className="kicker" style={{ marginBottom: 18 }}>STRATEGY PARAMETERS</div>
          <ParamSlider label="Min. confidence" value={confMin} min={40} max={95} step={5} unit="%" onChange={setConfMin}></ParamSlider>
          <ParamSlider label="Holding period" value={holdDays} min={1} max={21} step={1} unit="d" onChange={setHoldDays}></ParamSlider>
          <ParamSlider label="Stop loss" value={stopPct} min={2} max={15} step={1} unit="%" onChange={setStopPct}></ParamSlider>
          <div className="kicker" style={{ margin: "20px 0 4px" }}>SIGNAL SOURCES</div>
          <SourceToggle label="Technicals (25+)" on={sources.tech} onChange={(v) => setSource("tech", v)}></SourceToggle>
          <SourceToggle label="13F institutional flow" on={sources.flow} onChange={(v) => setSource("flow", v)}></SourceToggle>
          <SourceToggle label="Options sweeps" on={sources.options} onChange={(v) => setSource("options", v)}></SourceToggle>
          <SourceToggle label="Macro regime gate" on={sources.macro} onChange={(v) => setSource("macro", v)}></SourceToggle>
          <div style={{ marginTop: 20 }}>
            <button className={`btn ${compare ? "primary" : ""}`} style={{ width: "100%" }} onClick={() => setCompare(!compare)}>
              {compare ? "Comparing · Strategy B on" : "Compare with Strategy B"}
            </button>
            {compare && (
              <div style={{ fontSize: 11, color: "var(--text-faint)", marginTop: 8, lineHeight: 1.5 }}>
                <span style={{ color: "var(--neutral)" }}>— —</span> B: 55% conf · 3d hold · 8% stop · tech + options only
              </div>
            )}
          </div>
        </aside>

        {/* Results */}
        <main style={{ display: "flex", flexDirection: "column", gap: 14, minWidth: 0 }}>
          {btLoading ? (
            <div className="glass" style={{ padding: 20 }}>
              <SkelBlock h={160}></SkelBlock>
              <div style={{ marginTop: 14, display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 10 }}>
                {[0, 1, 2, 3].map((i) => <SkelBlock key={i} h={80}></SkelBlock>)}
              </div>
            </div>
          ) : realCards}

          <TrackTable rows={trackRecord}></TrackTable>

          <div className="glass" style={{ padding: "18px 20px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12, flexWrap: "wrap" }}>
              <span className="kicker">EQUITY CURVE · $100K START · 20Y SIMULATION</span>
              <span className="kicker" style={{ marginLeft: "auto", color: "var(--bear)" }}>■ DRAWDOWN SHADING</span>
            </div>
            <Defer ms={650} skeleton={<SkelBlock h={280}></SkelBlock>}>
              <EquityChart result={result} compare={cmpResult}></EquityChart>
            </Defer>
            <div style={{ display: "flex", gap: 18, marginTop: 10, flexWrap: "wrap" }}>
              <span className="mono" style={{ fontSize: 12, color: "var(--text-dim)" }}>
                Final equity <strong className="bull"><Num value={m.final} dp={0} prefix="$"></Num></strong>
              </span>
              <span className="mono" style={{ fontSize: 12, color: "var(--text-dim)" }}>
                Trades <strong style={{ color: "var(--text)" }}><Num value={m.trades} dp={0}></Num></strong>
              </span>
            </div>
          </div>

          <div className="bt-metrics">
            <MetricCard label="CAGR" value={m.cagr} dp={1} suffix="%" good={m.cagr > 0}></MetricCard>
            <MetricCard label="SHARPE" value={m.sharpe} dp={2} suffix="" good={m.sharpe > 0.8}></MetricCard>
            <MetricCard label="WIN RATE" value={m.winRate} dp={1} suffix="%" good={m.winRate > 55}></MetricCard>
            <MetricCard label="MAX DRAWDOWN" value={-m.maxDD} dp={1} suffix="%" good={m.maxDD < 12}></MetricCard>
          </div>

          {compare && cm && (
            <div className="glass" style={{ padding: "16px 20px" }}>
              <div className="kicker" style={{ marginBottom: 12 }}>STRATEGY COMPARISON</div>
              <div style={{ overflowX: "auto" }}>
                <table className="mono" style={{ width: "100%", borderCollapse: "collapse", fontSize: 12.5 }}>
                  <thead>
                    <tr style={{ textAlign: "right" }}>
                      <th style={{ textAlign: "left", padding: "6px 0", color: "var(--text-faint)", fontWeight: 500 }}></th>
                      <th style={{ padding: "6px 0", color: "var(--bull)", fontWeight: 600 }}>A · current</th>
                      <th style={{ padding: "6px 12px 6px 28px", color: "var(--neutral)", fontWeight: 600 }}>B · preset</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[
                      ["CAGR", `${m.cagr.toFixed(1)}%`, `${cm.cagr.toFixed(1)}%`, m.cagr >= cm.cagr],
                      ["Sharpe", m.sharpe.toFixed(2), cm.sharpe.toFixed(2), m.sharpe >= cm.sharpe],
                      ["Win rate", `${m.winRate.toFixed(1)}%`, `${cm.winRate.toFixed(1)}%`, m.winRate >= cm.winRate],
                      ["Max drawdown", `−${m.maxDD.toFixed(1)}%`, `−${cm.maxDD.toFixed(1)}%`, m.maxDD <= cm.maxDD],
                      ["Final equity", `$${Math.round(m.final).toLocaleString()}`, `$${Math.round(cm.final).toLocaleString()}`, m.final >= cm.final],
                    ].map(([label, a, b, aWins], i) => (
                      <tr key={i} style={{ borderTop: "1px solid var(--line-soft)", textAlign: "right" }}>
                        <td style={{ textAlign: "left", padding: "8px 0", color: "var(--text-dim)", fontFamily: "var(--font-sans)" }}>{label}</td>
                        <td style={{ padding: "8px 0", color: aWins ? "var(--bull)" : "var(--text)", fontWeight: aWins ? 700 : 400 }}>{a}</td>
                        <td style={{ padding: "8px 12px 8px 28px", color: !aWins ? "var(--neutral)" : "var(--text)", fontWeight: !aWins ? 700 : 400 }}>{b}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
          <div style={{ fontSize: 10.5, color: "var(--text-ghost)", lineHeight: 1.5 }}>
            Simulated results on historical data. Educational only — not financial advice. Past performance does not predict future results.
          </div>
        </main>
      </div>
    </div>
  );
}

Object.assign(window, { PageBacktest });
