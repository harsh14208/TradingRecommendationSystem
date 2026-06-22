/* global React */
// SIGNAL.TRADE cinematic — Backtest Lab (revised).
// Purpose: "Evidence for the Signal.Trade edge."
//   1. Canonical 23-year research backtest (hero)
//   2. Live forward-performance panel with honest IS/live gap
//   3. Lightweight what-if simulator (date range + entry policy)
//   4. Diagnostic tabs: sources, tickers, track record, correlation, calibration, alpha decay, ML model
const { useState: bUseState, useEffect: bUseEffect, useMemo: bUseMemo } = React;

const RESEARCH_ENDPOINT = "/api/signals/backtest/research";
const LIVE_ENDPOINT = "/api/signals/backtest";
const HORIZONS_ENDPOINT = "/api/signals/backtest/horizons";
const TRACK_ENDPOINT = "/api/signals/track-record";
const SOURCES_ENDPOINT = "/api/accuracy/sources";
const TICKERS_ENDPOINT = "/api/accuracy/tickers";
const CORR_ENDPOINT = "/api/signals/correlation";
const CALIB_ENDPOINT = "/api/signals/backtest/calibration";
const DECAY_ENDPOINT = "/api/signals/alpha-decay";
const ML_ENDPOINT = "/api/ml/status";
const SIM_ENDPOINT = "/api/signals/backtest/simulate";

const TABS = [
  ["summary", "Summary"],
  ["sources", "By Source"],
  ["tickers", "By Ticker"],
  ["track", "Track Record"],
  ["corr", "Correlation"],
  ["calib", "Calibration"],
  ["decay", "Alpha Decay"],
  ["model", "ML Model"],
];

function fmtPct(v, dp = 2) {
  if (v == null || Number.isNaN(v)) return "—";
  return `${v >= 0 ? "+" : ""}${v.toFixed(dp)}%`;
}
function fmtWr(v) {
  if (v == null || Number.isNaN(v)) return "—";
  return `${v.toFixed(1)}%`;
}
function colorWr(v) {
  if (v == null) return "var(--text-faint)";
  return v >= 60 ? "var(--bull)" : v >= 45 ? "var(--warn)" : "var(--bear)";
}
function colorRet(v) {
  if (v == null) return "var(--text-faint)";
  return v >= 0 ? "var(--bull)" : "var(--bear)";
}

function Section({ title, subtitle, children }) {
  return (
    <section style={{ marginBottom: 36 }}>
      <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", gap: 16, flexWrap: "wrap", marginBottom: 16 }}>
        <div>
          <h2 style={{ fontSize: 18, fontWeight: 700, margin: 0 }}>{title}</h2>
          {subtitle && <div style={{ fontSize: 12, color: "var(--text-faint)", marginTop: 4 }}>{subtitle}</div>}
        </div>
      </div>
      {children}
    </section>
  );
}

function Card({ children, style }) {
  return <div className="glass" style={{ padding: 18, borderRadius: 12, ...style }}>{children}</div>;
}

function Metric({ label, value, sub, color }) {
  return (
    <Card style={{ display: "flex", flexDirection: "column", gap: 6 }}>
      <div className="kicker" style={{ fontSize: 10 }}>{label}</div>
      <div className="mono" style={{ fontSize: 26, fontWeight: 700, color: color || "var(--text)", lineHeight: 1 }}>{value}</div>
      {sub && <div style={{ fontSize: 10.5, color: "var(--text-faint)" }}>{sub}</div>}
    </Card>
  );
}

function EquityChart({ curve, height = 260 }) {
  const w = 760;
  const h = height;
  const values = curve.map((p) => (typeof p === "number" ? p : p.value));
  const dates = curve.map((p) => (typeof p === "number" ? null : p.date));
  const min = Math.min(...values);
  const max = Math.max(...values);
  const rng = max - min || 1;
  const pts = values.map((v, i) => [(i / (values.length - 1)) * w, h - 16 - ((v - min) / rng) * (h - 40)]);
  const d = pts.map((p, i) => `${i ? "L" : "M"}${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(" ");

  let peak = values[0];
  const peakPts = values.map((v, i) => { if (v > peak) peak = v; return [(i / (values.length - 1)) * w, h - 16 - ((peak - min) / rng) * (h - 40)]; });
  const ddPath = peakPts.map((p, i) => `${i ? "L" : "M"}${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(" ")
    + " " + [...pts].reverse().map((p) => `L${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(" ") + " Z";

  const startLabel = dates[0] || "";
  const endLabel = dates[dates.length - 1] || "";

  return (
    <div style={{ position: "relative" }}>
      <svg viewBox={`0 0 ${w} ${h}`} style={{ width: "100%", height: "auto", display: "block" }}>
        <defs>
          <linearGradient id="eqfill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#22d3ee" stopOpacity="0.16"></stop>
            <stop offset="100%" stopColor="#22d3ee" stopOpacity="0"></stop>
          </linearGradient>
        </defs>
        <path d={ddPath} fill="rgba(251,77,109,0.10)"></path>
        <path d={`${d} L${w},${h} L0,${h} Z`} fill="url(#eqfill)"></path>
        <path d={d} fill="none" stroke="var(--bull)" strokeWidth="1.8" strokeLinejoin="round"></path>
      </svg>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 10, color: "var(--text-faint)", fontFamily: "var(--font-mono)", padding: "0 4px" }}>
        <span>{startLabel}</span>
        <span>{endLabel}</span>
      </div>
    </div>
  );
}

function Disclosure() {
  const [open, setOpen] = bUseState(false);
  return (
    <div style={{ background: "rgba(251,191,36,0.08)", border: "1px solid rgba(251,191,36,0.25)", borderRadius: 10, padding: "14px 16px", marginTop: 18 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, cursor: "pointer" }} onClick={() => setOpen(!open)}>
        <span style={{ fontSize: 16 }}>⚠️</span>
        <div style={{ flex: 1, fontSize: 13, fontWeight: 600 }}>Honest disclosure: live results are below the in-sample backtest</div>
        <span style={{ fontSize: 12, color: "var(--text-faint)" }}>{open ? "▾" : "▸"}</span>
      </div>
      {open && (
        <div style={{ fontSize: 12, color: "var(--text-dim)", lineHeight: 1.7, marginTop: 12 }}>
          <p>The 23-year in-sample (IS) backtest is the best historical evidence we have, but it is not a guarantee. Since launch, live performance has run below IS for known reasons:</p>
          <ul style={{ margin: "8px 0 8px 18px" }}>
            <li><strong>Regime mismatch:</strong> the live period (2022+) is dominated by rate-hike macro conditions where the strategy has historically struggled.</li>
            <li><strong>Delivery leaks fixed in v8.4:</strong> sector unblock and SELL bypass leaked alpha; the clean post-fix cohort is much closer to IS.</li>
            <li><strong>Overfitting ceiling:</strong> deflated Sharpe fails at 744 trials — the IS backtest is already about as good as we can tune it.</li>
          </ul>
          <p>Broker auto-execution should remain on paper until live win rate is consistently above 55% and all readiness criteria in SIGNAL_VALIDATION.md are met.</p>
        </div>
      )}
    </div>
  );
}

function ResearchHero({ data }) {
  if (!data) return <div className="skel" style={{ height: 360 }}></div>;
  const s = data.summary || {};
  const canon = data.canon || {};
  const curve = data.equity_curve || [];
  return (
    <Section title="Research Track Record" subtitle={`${canon.period || "23-year"} in-sample backtest · ${canon.version || ""} canon`}>
      <Card>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(140px, 1fr))", gap: 12, marginBottom: 18 }}>
          <Metric label="Trades" value={s.total_trades ?? canon.total_trades ?? "—"} color="var(--text)" />
          <Metric label="Win rate" value={fmtWr(s.win_rate ?? canon.win_rate)} color={colorWr(s.win_rate ?? canon.win_rate)} />
          <Metric label="Avg return / trade" value={fmtPct(s.avg_return)} color={colorRet(s.avg_return)} />
          <Metric label="Sharpe" value={s.sharpe ?? canon.sharpe ?? "—"} />
          <Metric label="Max drawdown" value={fmtPct(s.max_drawdown_pct ?? canon.max_drawdown_pct, 2)} color="var(--bear)" />
          <Metric label="CAGR" value={fmtPct(s.cagr_pct)} color={colorRet(s.cagr_pct)} />
        </div>
        <EquityChart curve={curve} />
      </Card>
      <Disclosure />
    </Section>
  );
}

function LivePanel({ data, horizons, track, loading }) {
  if (loading) return <div className="skel" style={{ height: 200 }}></div>;
  const s = data || {};
  const hasData = s.total > 0;
  const liveWr = s.win_rate ?? null;
  const isWr = 69.1;
  const gap = liveWr != null ? liveWr - isWr : null;

  return (
    <Section title="Live Forward Test" subtitle="Resolved signals since launch, phantom-win corrected">
      <Card>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(140px, 1fr))", gap: 12, marginBottom: 18 }}>
          <Metric label="Resolved signals" value={s.resolved ?? 0} color="var(--text)" />
          <Metric label="Live win rate" value={fmtWr(liveWr)} color={colorWr(liveWr)} />
          <Metric label="Avg return" value={fmtPct(s.avg_return)} color={colorRet(s.avg_return)} />
          <Metric label="Live Sharpe" value={s.sharpe ?? "—"} />
          <Metric label="IS vs live gap" value={gap != null ? `${gap >= 0 ? "+" : ""}${gap.toFixed(1)}pp` : "—"} color={gap != null && gap >= 0 ? "var(--bull)" : "var(--warn)"} />
          <Metric label="Max DD" value={fmtPct(s.max_drawdown_pct)} color="var(--bear)" />
        </div>

        {!hasData && (
          <div style={{ textAlign: "center", color: "var(--text-faint)", fontSize: 13, padding: "24px 0" }}>
            No resolved live signals yet. Use the simulator below to replay historical signals, or backfill outcomes.
          </div>
        )}

        {horizons && horizons.length > 0 && (
          <div>
            <div className="kicker" style={{ marginBottom: 10 }}>By hold period</div>
            <div style={{ display: "grid", gridTemplateColumns: `repeat(${Math.min(horizons.length, 4)}, 1fr)`, gap: 10 }}>
              {horizons.map((h) => (
                <div key={h.horizon} style={{ background: "var(--bg-2)", borderRadius: 8, padding: 12, border: "1px solid var(--line)" }}>
                  <div style={{ fontSize: 10, color: "var(--text-faint)", fontFamily: "var(--font-mono)", textTransform: "uppercase", marginBottom: 6 }}>{h.horizon} · {h.n} signals</div>
                  <div className="mono" style={{ fontSize: 18, fontWeight: 700, color: colorWr(h.win_rate) }}>{fmtWr(h.win_rate)}</div>
                  <div className="mono" style={{ fontSize: 12, color: colorRet(h.avg_return) }}>{fmtPct(h.avg_return)} avg</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </Card>
    </Section>
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
  const sharpe = sd > 0 ? (mean / sd) * Math.sqrt(52) : 0;
  const total = curve[curve.length - 1] / start - 1;
  const firstDate = sorted[0].date ? new Date(sorted[0].date) : null;
  const lastDate = sorted[sorted.length - 1].date ? new Date(sorted[sorted.length - 1].date) : null;
  const years = firstDate && lastDate ? Math.max(0.25, (lastDate - firstDate) / (365.25 * 24 * 3600 * 1000)) : n / 52;
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
      timeoutRate: sim.timeout_rate,
    },
  };
}

function SimulatorPanel() {
  const [start, setStart] = bUseState("");
  const [end, setEnd] = bUseState("");
  const [policy, setPolicy] = bUseState("market");
  const [maxSig, setMaxSig] = bUseState(200);
  const [sim, setSim] = bUseState(null);
  const [loading, setLoading] = bUseState(false);

  const run = () => {
    setLoading(true);
    const params = new URLSearchParams();
    params.set("entry_policy", policy);
    params.set("max_signals", String(maxSig));
    if (start) params.set("start_date", start);
    if (end) params.set("end_date", end);
    apiFetch(`${SIM_ENDPOINT}?${params.toString()}`)
      .then(setSim)
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  const result = bUseMemo(() => buildSimResult(sim), [sim]);

  return (
    <Section title="What-If Simulator" subtitle="Replay historical sent signals with realistic execution">
      <Card>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 12, alignItems: "center", marginBottom: 16 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span className="kicker">FROM</span>
            <input type="date" value={start} onChange={(e) => setStart(e.target.value)} style={{ background: "var(--bg-2)", border: "1px solid var(--line)", borderRadius: 4, color: "var(--text)", padding: "5px 8px", fontFamily: "var(--font-mono)", fontSize: 11 }} />
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span className="kicker">TO</span>
            <input type="date" value={end} onChange={(e) => setEnd(e.target.value)} style={{ background: "var(--bg-2)", border: "1px solid var(--line)", borderRadius: 4, color: "var(--text)", padding: "5px 8px", fontFamily: "var(--font-mono)", fontSize: 11 }} />
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span className="kicker">ENTRY</span>
            <select value={policy} onChange={(e) => setPolicy(e.target.value)} style={{ background: "var(--bg-2)", border: "1px solid var(--line)", borderRadius: 4, color: "var(--text)", padding: "5px 8px", fontFamily: "var(--font-mono)", fontSize: 11 }}>
              <option value="market">Market (next open + slippage)</option>
              <option value="next_open">Next open (no slippage)</option>
              <option value="limit">Limit at signal entry</option>
            </select>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span className="kicker">MAX</span>
            <input type="number" min={1} max={2000} value={maxSig} onChange={(e) => setMaxSig(Number(e.target.value))} style={{ width: 70, background: "var(--bg-2)", border: "1px solid var(--line)", borderRadius: 4, color: "var(--text)", padding: "5px 8px", fontFamily: "var(--font-mono)", fontSize: 11 }} />
          </div>
          <button className="btn primary" style={{ fontSize: 12, padding: "6px 16px" }} onClick={run} disabled={loading}>
            {loading ? "Running…" : "Run Simulation"}
          </button>
        </div>

        {result && (
          <>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(130px, 1fr))", gap: 12, marginBottom: 18 }}>
              <Metric label="Trades" value={result.metrics.trades} />
              <Metric label="Win rate" value={fmtWr(result.metrics.winRate)} color={colorWr(result.metrics.winRate)} />
              <Metric label="CAGR" value={fmtPct(result.metrics.cagr)} color={colorRet(result.metrics.cagr)} />
              <Metric label="Sharpe" value={result.metrics.sharpe.toFixed(2)} />
              <Metric label="Max DD" value={fmtPct(result.metrics.maxDD)} color="var(--bear)" />
              <Metric label="Cost drag" value={fmtPct(result.metrics.costDrag, 3)} />
            </div>
            <EquityChart curve={result.curve} height={200} />
          </>
        )}

        {!result && !loading && (
          <div style={{ textAlign: "center", color: "var(--text-faint)", fontSize: 12, padding: "18px 0" }}>
            Pick a date range and entry policy, then click Run Simulation.
          </div>
        )}
        {loading && <div style={{ textAlign: "center", color: "var(--text-faint)", fontSize: 12, padding: "18px 0" }}>Loading price history for every signal…</div>}
      </Card>
    </Section>
  );
}

function BtTable({ title, cols, rows, colors }) {
  if (!rows || rows.length === 0) return null;
  return (
    <div>
      {title && <div className="kicker" style={{ marginBottom: 10 }}>{title}</div>}
      <div style={{ overflowX: "auto" }}>
        <table className="mono" style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
          <thead>
            <tr style={{ textAlign: "right", color: "var(--text-faint)" }}>
              {cols.map((c, i) => <th key={i} style={{ padding: "7px 8px", fontWeight: 500, textAlign: i === 0 ? "left" : "right" }}>{c}</th>)}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, ri) => (
              <tr key={ri} style={{ borderTop: "1px solid var(--line-soft)" }}>
                {row.map((cell, ci) => {
                  const color = colors && colors[ci] ? (typeof colors[ci] === "function" ? colors[ci](cell, ri) : colors[ci]) : null;
                  return <td key={ci} style={{ padding: "8px", textAlign: ci === 0 ? "left" : "right", color: color || "var(--text-dim)" }}>{cell}</td>;
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function CalibrationChart({ data }) {
  const w = 360, h = 160, pad = { t: 10, r: 10, b: 24, l: 34 };
  const innerW = w - pad.l - pad.r, innerH = h - pad.t - pad.b;
  const pts = data.map((d, i) => ({
    x: pad.l + (i / (data.length - 1)) * innerW,
    y: pad.t + innerH - ((d.actual || 0) / 100) * innerH,
    px: pad.l + (i / (data.length - 1)) * innerW,
    py: pad.t + innerH - ((d.predicted || 0) / 100) * innerH,
  }));
  const diag = `M${pad.l},${pad.t + innerH} L${pad.l + innerW},${pad.t}`;
  return (
    <svg viewBox={`0 0 ${w} ${h}`} style={{ width: "100%", maxWidth: 480, height: "auto", display: "block" }}>
      {[0, 25, 50, 75, 100].map((t) => (
        <g key={t}>
          <line x1={pad.l} x2={pad.l + innerW} y1={pad.t + innerH - (t / 100) * innerH} y2={pad.t + innerH - (t / 100) * innerH} stroke="rgba(255,255,255,0.05)" />
          <text x={pad.l - 6} y={pad.t + innerH - (t / 100) * innerH + 3} textAnchor="end" fontSize="9" fill="var(--text-faint)">{t}%</text>
        </g>
      ))}
      <path d={diag} stroke="rgba(255,255,255,0.15)" strokeDasharray="3 3" />
      {pts.map((p, i) => (
        <g key={i}>
          <line x1={p.px} x2={p.px} y1={p.py} y2={p.y} stroke={p.y < p.py ? "var(--bear)" : "var(--bull)"} strokeWidth="2" />
          <circle cx={p.px} cy={p.py} r="3" fill="var(--text-faint)" />
          <circle cx={p.px} cy={p.y} r="3" fill="var(--accent)" />
        </g>
      ))}
    </svg>
  );
}

function DiagnosticsTabs({ data, horizons, accuracy, trackRec, corr, calib, decay, ml, loading }) {
  const [tab, setTab] = bUseState("summary");
  const fmtPct2 = (v) => v != null ? `${v >= 0 ? "+" : ""}${v.toFixed(2)}%` : "—";
  const fmtWr2 = (v) => v != null ? `${v.toFixed(1)}%` : "—";

  if (loading) return <div className="skel" style={{ height: 200 }}></div>;

  return (
    <Section title="Diagnostics" subtitle="Decompose performance by source, ticker, horizon, and model calibration">
      <Card style={{ padding: 0, overflow: "hidden" }}>
        <div style={{ display: "flex", gap: 0, borderBottom: "1px solid var(--line)", padding: "0 16px", background: "var(--bg-1)", overflowX: "auto" }}>
          {TABS.map(([id, label]) => (
            <button key={id} onClick={() => setTab(id)} style={{ padding: "10px 14px", fontSize: 11, fontFamily: "var(--font-mono)", fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase", background: "none", border: "none", cursor: "pointer", borderBottom: tab === id ? "2px solid var(--accent)" : "2px solid transparent", color: tab === id ? "var(--accent)" : "var(--text-faint)", marginBottom: -1, whiteSpace: "nowrap" }}>
              {label}
            </button>
          ))}
        </div>
        <div style={{ padding: 20 }}>
          {tab === "summary" && (
            <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
              <BtTable title="By signal direction" cols={["Direction", "Signals", "Win Rate", "Avg Return", "Avg Win", "Avg Loss"]}
                rows={(data?.by_action || []).map((r) => [r.action, r.count, fmtWr2(r.win_rate), fmtPct2(r.avg_return), fmtPct2(r.avg_win), fmtPct2(r.avg_loss)])}
                colors={[null, null, (_, ri) => colorWr((data?.by_action || [])[ri]?.win_rate), (_, ri) => colorRet((data?.by_action || [])[ri]?.avg_return), "var(--bull)", "var(--bear)"]} />
              <BtTable title="By data source" cols={["Source", "Signals", "Win Rate", "Avg Return"]}
                rows={(data?.by_source || []).map((r) => [r.source, r.count, fmtWr2(r.win_rate), fmtPct2(r.avg_return)])}
                colors={[null, null, (_, ri) => colorWr((data?.by_source || [])[ri]?.win_rate), (_, ri) => colorRet((data?.by_source || [])[ri]?.avg_return)]} />
              <BtTable title="By confidence tier" cols={["Tier", "Signals", "Win Rate", "Avg Return"]}
                rows={(data?.by_confidence || []).map((r) => [r.tier, r.count, fmtWr2(r.win_rate), fmtPct2(r.avg_return)])}
                colors={[null, null, (_, ri) => colorWr((data?.by_confidence || [])[ri]?.win_rate), (_, ri) => colorRet((data?.by_confidence || [])[ri]?.avg_return)]} />
            </div>
          )}

          {tab === "sources" && (
            <BtTable title="Win rate by data source" cols={["Source", "Signals", "Win Rate", "Avg Return"]}
              rows={(accuracy?.sources || []).map((r) => [r.source, r.total, fmtWr2(r.win_rate), fmtPct2(r.avg_ret)])}
              colors={[null, null, (_, ri) => colorWr((accuracy?.sources || [])[ri]?.win_rate), (_, ri) => colorRet((accuracy?.sources || [])[ri]?.avg_ret)]} />
          )}

          {tab === "tickers" && (
            <BtTable title="Win rate by ticker" cols={["Ticker", "Signals", "Win Rate", "Avg Return", "Top Sources"]}
              rows={(accuracy?.tickers || []).map((r) => [r.ticker, r.total, fmtWr2(r.win_rate), fmtPct2(r.avg_ret), (r.top_sources || []).join(", ")])}
              colors={[null, null, (_, ri) => colorWr((accuracy?.tickers || [])[ri]?.win_rate), (_, ri) => colorRet((accuracy?.tickers || [])[ri]?.avg_ret), null]} />
          )}

          {tab === "track" && (
            <BtTable title="Per-ticker track record" cols={["Ticker", "Signals", "Win Rate", "Avg Return", "Sharpe"]}
              rows={(trackRec || []).map((r) => [r.ticker, r.signals ?? r.total, fmtWr2(r.win_rate), fmtPct2(r.avg_return), r.sharpe?.toFixed(2) ?? "—"])}
              colors={[null, null, (_, ri) => colorWr((trackRec || [])[ri]?.win_rate), (_, ri) => colorRet((trackRec || [])[ri]?.avg_return), null]} />
          )}

          {tab === "corr" && (
            <BtTable title="Source co-occurrence · joint win rates" cols={["Source A", "Source B", "Joint Signals", "Joint Win Rate"]}
              rows={((corr?.pairs ?? corr) || []).map((r) => [r.a ?? r.source_a, r.b ?? r.source_b, r.count, fmtWr2(r.win_rate)])}
              colors={[null, null, null, (_, ri) => colorWr(((corr?.pairs ?? corr) || [])[ri]?.win_rate)]} />
          )}

          {tab === "calib" && (
            <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
              <div style={{ fontSize: 12, color: "var(--text-dim)", maxWidth: 620 }}>
                Each bar shows predicted confidence vs actual win rate. A well-calibrated model has dots near the diagonal. Bars above the predicted dot = overconfident.
              </div>
              {calib && calib.length > 0 && <CalibrationChart data={calib} />}
              <BtTable title="Calibration by bucket" cols={["Bucket", "Predicted", "Actual", "Signals", "Gap"]}
                rows={(calib || []).map((r) => [r.bucket, `${r.predicted.toFixed(1)}%`, fmtWr2(r.actual), r.count, <span style={{ color: Math.abs(r.gap) > 10 ? "var(--bear)" : Math.abs(r.gap) > 5 ? "var(--warn)" : "var(--bull)" }}>{r.gap > 0 ? `+${r.gap.toFixed(1)}%` : `${r.gap.toFixed(1)}%`}</span>])}
                colors={[null, null, (_, ri) => colorWr((calib || [])[ri]?.actual), null, null]} />
            </div>
          )}

          {tab === "decay" && (
            <div>
              <div style={{ fontSize: 12, color: "var(--text-dim)", marginBottom: 16, maxWidth: 620 }}>
                Alpha decay by signal source — win rate and average return at each holding horizon. Sources that peak at 1d are short-lived; sources still strong at 14d have durable edge.
              </div>
              {decay && Object.keys(decay).length > 0 ? (
                <BtTable title="Alpha decay by source" cols={["Source", "N", "1d Win%", "1d Ret", "3d Win%", "3d Ret", "7d Win%", "7d Ret", "14d Win%", "14d Ret"]}
                  rows={Object.entries(decay)
                    .sort((a, b) => (b[1].h7d?.win_rate ?? 0) - (a[1].h7d?.win_rate ?? 0))
                    .map(([src, d]) => {
                      const h = (k) => d[k];
                      const wr = (v) => v?.win_rate != null ? `${v.win_rate.toFixed(1)}%` : "—";
                      const ret = (v) => v?.avg_ret != null ? `${v.avg_ret >= 0 ? "+" : ""}${v.avg_ret.toFixed(2)}%` : "—";
                      return [src, d.n, wr(h("h1d")), ret(h("h1d")), wr(h("h3d")), ret(h("h3d")), wr(h("h7d")), ret(h("h7d")), wr(h("h14d")), ret(h("h14d"))];
                    })}
                  colors={[null, null,
                    (_, ri) => colorWr(Object.values(decay)[ri]?.h1d?.win_rate),
                    (_, ri) => colorRet(Object.values(decay)[ri]?.h1d?.avg_ret),
                    (_, ri) => colorWr(Object.values(decay)[ri]?.h3d?.win_rate),
                    (_, ri) => colorRet(Object.values(decay)[ri]?.h3d?.avg_ret),
                    (_, ri) => colorWr(Object.values(decay)[ri]?.h7d?.win_rate),
                    (_, ri) => colorRet(Object.values(decay)[ri]?.h7d?.avg_ret),
                    (_, ri) => colorWr(Object.values(decay)[ri]?.h14d?.win_rate),
                    (_, ri) => colorRet(Object.values(decay)[ri]?.h14d?.avg_ret),
                  ]} />
              ) : <div style={{ color: "var(--text-faint)", fontSize: 12 }}>No alpha decay data yet.</div>}
            </div>
          )}

          {tab === "model" && <MLModelTab />}
        </div>
      </Card>
    </Section>
  );
}

function MLModelTab() {
  const [ml, setMl] = bUseState(null);
  const [loading, setLoading] = bUseState(true);
  const [err, setErr] = bUseState("");

  bUseEffect(() => {
    let alive = true;
    setLoading(true);
    apiFetch(ML_ENDPOINT)
      .then((d) => { if (alive) setMl(d); })
      .catch(() => { if (alive) setErr("Could not load ML model status."); })
      .finally(() => { if (alive) setLoading(false); });
    return () => { alive = false; };
  }, []);

  if (loading) return <div style={{ color: "var(--text-faint)", fontSize: 12 }}>Loading…</div>;
  if (err) return <div style={{ color: "var(--bear)", fontSize: 12 }}>{err}</div>;
  if (!ml) return null;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(130px, 1fr))", gap: 12 }}>
        <Metric label="Model version" value={ml.model_version ?? "—"} />
        <Metric label="AUC" value={ml.auc?.toFixed(3) ?? "—"} />
        <Metric label="Features" value={ml.n_features ?? "—"} />
        <Metric label="Training samples" value={ml.n_samples ?? "—"} />
      </div>
      {ml.feature_importance && ml.feature_importance.length > 0 && (
        <BtTable title="Top feature importances" cols={["Feature", "Importance"]}
          rows={ml.feature_importance.slice(0, 15).map((f) => [f.feature, f.importance.toFixed(4)])} />
      )}
    </div>
  );
}

function PageBacktest() {
  const [research, setResearch] = bUseState(null);
  const [data, setData] = bUseState(null);
  const [horizons, setHorizons] = bUseState([]);
  const [accuracy, setAccuracy] = bUseState({ sources: [], tickers: [] });
  const [trackRec, setTrackRec] = bUseState([]);
  const [corr, setCorr] = bUseState(null);
  const [calib, setCalib] = bUseState([]);
  const [decay, setDecay] = bUseState({});
  const [loading, setLoading] = bUseState(true);

  bUseEffect(() => {
    let alive = true;
    setLoading(true);
    apiFetch(RESEARCH_ENDPOINT)
      .then((r) => { if (alive) setResearch(r); })
      .catch(() => {});

    Promise.all([
      apiFetch(LIVE_ENDPOINT),
      apiFetch(HORIZONS_ENDPOINT),
      apiFetch(SOURCES_ENDPOINT),
      apiFetch(TICKERS_ENDPOINT),
      apiFetch(TRACK_ENDPOINT),
      apiFetch(CORR_ENDPOINT),
      apiFetch(CALIB_ENDPOINT),
      apiFetch(DECAY_ENDPOINT),
    ]).then(([d, h, src, tkr, tr, cr, cal, dc]) => {
      if (!alive) return;
      setData(d);
      setHorizons((h || []).filter((x) => x.n > 0));
      setAccuracy({ sources: src || [], tickers: tkr || [] });
      setTrackRec(tr || []);
      setCorr(cr);
      setCalib(cal || []);
      setDecay(dc || {});
    }).catch(() => {}).finally(() => { if (alive) setLoading(false); });

    return () => { alive = false; };
  }, []);

  return (
    <div className="page" style={{ maxWidth: 980, margin: "0 auto", padding: "28px 22px 80px" }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 22 }}>
        <div>
          <div className="crumb" style={{ marginBottom: 4 }}>RESEARCH / BACKTEST</div>
          <h1 style={{ fontSize: 28, fontWeight: 800, margin: 0, letterSpacing: "-0.02em" }}>Evidence Lab</h1>
        </div>
      </div>

      <ResearchHero data={research} />
      <LivePanel data={data} horizons={horizons} track={trackRec} loading={loading} />
      <SimulatorPanel />
      <DiagnosticsTabs
        data={data}
        horizons={horizons}
        accuracy={accuracy}
        trackRec={trackRec}
        corr={corr}
        calib={calib}
        decay={decay}
        loading={loading}
      />
    </div>
  );
}

Object.assign(window, { PageBacktest });
