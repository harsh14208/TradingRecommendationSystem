/* global React */
// SIGNAL.TRADE cinematic — Backtest Lab.
// Fetches real /api/signals/backtest, /api/signals/backtest/horizons,
// /api/signals/track-record and /api/signals/backtest/simulate for the
// headline equity curve and metrics (realistic trade replay, not a toy sim).
const { useState: bUseState, useEffect: bUseEffect, useMemo: bUseMemo } = React;

function EquityChart({ result }) {
  const w = 760, h = 300;
  const all = result.curve;
  const min = Math.min(...all), max = Math.max(...all);
  const rng = max - min || 1;
  const toPts = (curve) => curve.map((v, i) => [(i / (curve.length - 1)) * w, h - 18 - ((v - min) / rng) * (h - 44)]);
  const pts = toPts(result.curve);
  const d = pts.map((p, i) => `${i ? "L" : "M"}${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(" ");

  let peak = result.curve[0];
  const peakPts = result.curve.map((v, i) => { if (v > peak) peak = v; return [(i / (result.curve.length - 1)) * w, h - 18 - ((peak - min) / rng) * (h - 44)]; });
  const ddPath = peakPts.map((p, i) => `${i ? "L" : "M"}${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(" ")
    + " " + [...pts].reverse().map((p) => `L${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(" ") + " Z";

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
    </svg>
  );
}

function MetricCard({ label, value, sub, good }) {
  return (
    <div className="glass glass-hover" style={{ padding: "16px 18px" }}>
      <div className="kicker" style={{ marginBottom: 8 }}>{label}</div>
      <div className="mono" style={{ fontSize: 24, fontWeight: 700, color: good ? "var(--bull)" : "var(--bear)" }}>{value}</div>
      {sub && <div style={{ fontSize: 10.5, color: "var(--text-faint)", marginTop: 4 }}>{sub}</div>}
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

function buildSimResult(sim) {
  if (!sim || !Array.isArray(sim.signals) || sim.signals.length === 0) return null;
  const sorted = [...sim.signals].sort((a, b) => (a.date || "").localeCompare(b.date || ""));
  const returns = sorted.map((s) => s.net_pct ?? s.gross_pct ?? 0);
  const start = 100000;
  const curve = [start];
  let peak = start, maxDD = 0;
  for (const r of returns) {
    const v = curve[curve.length - 1] * (1 + r / 100);
    curve.push(v);
    if (v > peak) peak = v;
    const dd = (peak - v) / peak;
    if (dd > maxDD) maxDD = dd;
  }

  const n = returns.length;
  const mean = returns.reduce((a, b) => a + b, 0) / n;
  const variance = returns.reduce((a, b) => a + b * b, 0) / n - mean * mean;
  const sd = Math.sqrt(Math.max(0, variance));
  // Same trade-based annualization convention used by the live backtest engine.
  const sharpe = sd > 0 ? (mean / sd) * Math.sqrt(52) : 0;

  const total = curve[curve.length - 1] / start - 1;
  const firstDate = sorted[0].date ? new Date(sorted[0].date) : null;
  const lastDate = sorted[sorted.length - 1].date ? new Date(sorted[sorted.length - 1].date) : null;
  const years = firstDate && lastDate
    ? Math.max(0.25, (lastDate - firstDate) / (365.25 * 24 * 3600 * 1000))
    : n / 52;
  const cagr = Math.pow(1 + total, 1 / years) - 1;
  const wins = returns.filter((r) => r > 0).length;

  return {
    curve,
    metrics: {
      cagr: cagr * 100,
      sharpe,
      winRate: (wins / n) * 100,
      maxDD: maxDD * 100,
      trades: n,
      final: curve[curve.length - 1],
      costDrag: sim.cost_drag_avg,
      stopRate: sim.stop_hit_rate,
      targetRate: sim.target_hit_rate,
    },
  };
}

function PageBacktest() {
  const [btSummary, setBtSummary] = bUseState(null);
  const [horizons, setHorizons] = bUseState([]);
  const [trackRecord, setTrackRecord] = bUseState([]);
  const [sim, setSim] = bUseState(null);
  const [btLoading, setBtLoading] = bUseState(true);

  bUseEffect(() => {
    let alive = true;
    setBtLoading(true);
    Promise.all([
      apiFetch("/api/signals/backtest"),
      apiFetch("/api/signals/backtest/horizons"),
      apiFetch("/api/signals/track-record"),
      apiFetch("/api/signals/backtest/simulate"),
    ]).then(([sum, hrs, trk, simResp]) => {
      if (!alive) return;
      if (sum && typeof sum === "object") setBtSummary(sum);
      if (Array.isArray(hrs)) setHorizons(hrs);
      if (Array.isArray(trk)) setTrackRecord(trk);
      if (simResp && typeof simResp === "object") setSim(simResp);
    }).catch(() => {}).finally(() => { if (alive) setBtLoading(false); });
    return () => { alive = false; };
  }, []);

  const simResult = bUseMemo(() => buildSimResult(sim), [sim]);
  const m = simResult ? simResult.metrics : null;

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
        <aside className="glass" style={{ padding: 20, alignSelf: "start" }}>
          <div className="kicker" style={{ marginBottom: 12 }}>TRADE-REPLAY ENGINE</div>
          <p style={{ fontSize: 12.5, color: "var(--text-dim)", lineHeight: 1.6, margin: 0 }}>
            The headline equity curve is built from the last {m ? m.trades : "—"} resolved signals.
            Entry is modelled at the next-day open with slippage, exit on stop/target hit or a 7-day timeout,
            and cost drag is subtracted.
          </p>
          <div style={{ marginTop: 18, display: "grid", gap: 10 }}>
            <MetricCard
              label="COST DRAG"
              value={m ? `${m.costDrag >= 0 ? "+" : ""}${m.costDrag.toFixed(2)}%` : "—"}
              sub="Slippage + commission"
              good={m ? m.costDrag < 0.5 : false}
            ></MetricCard>
            <MetricCard
              label="STOP HIT RATE"
              value={m ? `${m.stopRate.toFixed(1)}%` : "—"}
              sub="Per closed trade"
              good={m ? m.stopRate < 40 : false}
            ></MetricCard>
            <MetricCard
              label="TARGET HIT RATE"
              value={m ? `${m.targetRate.toFixed(1)}%` : "—"}
              sub="Per closed trade"
              good={m ? m.targetRate > 30 : false}
            ></MetricCard>
          </div>
        </aside>

        <main style={{ display: "flex", flexDirection: "column", gap: 14, minWidth: 0 }}>
          {/* Equity curve — graph first, then metrics */}
          <div className="glass" style={{ padding: "18px 20px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12, flexWrap: "wrap" }}>
              <span className="kicker">EQUITY CURVE · $100K START · TRADE-BY-TRADE REPLAY</span>
              <span className="kicker" style={{ marginLeft: "auto", color: "var(--bear)" }}>■ DRAWDOWN SHADING</span>
            </div>
            {btLoading || !simResult ? (
              <SkelBlock h={280}></SkelBlock>
            ) : (
              <>
                <EquityChart result={simResult}></EquityChart>
                <div style={{ display: "flex", gap: 18, marginTop: 10, flexWrap: "wrap" }}>
                  <span className="mono" style={{ fontSize: 12, color: "var(--text-dim)" }}>
                    Final equity <strong className="bull"><Num value={m.final} dp={0} prefix="$"></Num></strong>
                  </span>
                  <span className="mono" style={{ fontSize: 12, color: "var(--text-dim)" }}>
                    Trades <strong style={{ color: "var(--text)" }}><Num value={m.trades} dp={0}></Num></strong>
                  </span>
                </div>
              </>
            )}
          </div>

          <div className="bt-metrics">
            <MetricCard
              label="CAGR"
              value={m ? `${m.cagr.toFixed(1)}%` : "—"}
              sub="Annualized"
              good={m ? m.cagr > 0 : false}
            ></MetricCard>
            <MetricCard
              label="SHARPE"
              value={m ? m.sharpe.toFixed(2) : "—"}
              sub="Trade-based, √52"
              good={m ? m.sharpe > 0.8 : false}
            ></MetricCard>
            <MetricCard
              label="WIN RATE"
              value={m ? `${m.winRate.toFixed(1)}%` : "—"}
              sub="Net of costs"
              good={m ? m.winRate > 50 : false}
            ></MetricCard>
            <MetricCard
              label="MAX DRAWDOWN"
              value={m ? `−${m.maxDD.toFixed(1)}%` : "—"}
              sub="Peak-to-trough"
              good={m ? m.maxDD < 25 : false}
            ></MetricCard>
          </div>

          {/* Live backtest (resolved signals) + per-horizon + per-ticker */}
          {btLoading ? (
            <div className="glass" style={{ padding: 20 }}>
              <SkelBlock h={160}></SkelBlock>
              <div style={{ marginTop: 14, display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 10 }}>
                {[0, 1, 2, 3].map((i) => <SkelBlock key={i} h={80}></SkelBlock>)}
              </div>
            </div>
          ) : realCards}

          <TrackTable rows={trackRecord}></TrackTable>

          <div style={{ fontSize: 10.5, color: "var(--text-ghost)", lineHeight: 1.5 }}>
            Simulated results on historical data. Educational only — not financial advice. Past performance does not predict future results.
          </div>
        </main>
      </div>
    </div>
  );
}

Object.assign(window, { PageBacktest });
