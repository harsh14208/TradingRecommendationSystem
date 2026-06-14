/* global React */
// SIGNAL.TRADE cinematic — Track Record page (real audited stats).
// Derives aggregates from histSignals when available; falls back to mocks.
const { useMemo: tUseMemo } = React;

function TrackStat({ s }) {
  const col = s.tone === "up" ? "var(--bull)" : s.tone === "down" ? "var(--bear)" : "var(--text)";
  return (
    <div className="glass glass-hover" style={{ padding: "18px 20px" }}>
      <div className="kicker" style={{ marginBottom: 8 }}>{s.label}</div>
      <div className="mono" style={{ fontSize: 26, fontWeight: 700, color: col }}>{s.value}</div>
      <div style={{ fontSize: 11, color: "var(--text-faint)", marginTop: 4 }}>{s.sub}</div>
    </div>
  );
}

function MonthBars({ months }) {
  const ms = [...months].reverse();
  const max = Math.max(...ms.map((m) => m.win));
  return (
    <div style={{ display: "flex", alignItems: "flex-end", gap: 10, height: 110, padding: "0 4px" }}>
      {ms.map((m, i) => {
        const h = (m.win / max) * 100;
        const col = m.win >= 62 ? "var(--bull)" : "var(--neutral)";
        return (
          <div key={i} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: 6 }}>
            <span className="mono" style={{ fontSize: 10.5, fontWeight: 600, color: col }}>{m.win.toFixed(1)}%</span>
            <div style={{ width: "100%", height: `${h}%`, minHeight: 4, borderRadius: "3px 3px 0 0", background: `linear-gradient(180deg, ${col}, rgba(255,255,255,0.04))` }}></div>
            <span className="mono" style={{ fontSize: 9.5, color: "var(--text-faint)" }}>{m.m.split(" ")[0]}</span>
          </div>
        );
      })}
    </div>
  );
}

function fmtRet(v) { return v == null ? "—" : `${v >= 0 ? "+" : ""}${v.toFixed(2)}%`; }

function useTrackData(histSignals) {
  return tUseMemo(() => {
    const resolved = (histSignals || []).filter((s) => s.outcomePct != null);
    if (!resolved.length) return null;

    const total = resolved.length;
    const wins = resolved.filter((s) => s.outcomePct > 0);
    const losses = resolved.filter((s) => s.outcomePct <= 0);
    const winRate = total ? (wins.length / total) * 100 : 0;
    const avgReturn = total ? resolved.reduce((a, s) => a + s.outcomePct, 0) / total : 0;

    let peak = 0, maxDD = 0, cum = 0;
    for (const s of resolved) {
      cum += s.outcomePct;
      if (cum > peak) peak = cum;
      const dd = peak - cum;
      if (dd > maxDD) maxDD = dd;
    }

    const monthBuckets = {};
    for (const s of resolved) {
      const d = s.date || s.ts || s.created_at;
      if (!d) continue;
      const dt = new Date(d);
      const key = `${dt.toLocaleString("en-US", { month: "short" })} ${dt.getFullYear().toString().slice(-2)}`;
      if (!monthBuckets[key]) monthBuckets[key] = [];
      monthBuckets[key].push(s);
    }
    const months = Object.entries(monthBuckets).map(([m, sigs]) => {
      const w = sigs.filter((s) => s.outcomePct > 0);
      const l = sigs.filter((s) => s.outcomePct <= 0);
      const mean = sigs.reduce((a, s) => a + s.outcomePct, 0) / sigs.length;
      const std = sigs.length > 1 ? Math.sqrt(sigs.reduce((a, s) => a + Math.pow(s.outcomePct - mean, 2), 0) / (sigs.length - 1)) : 0;
      const sharpe = std > 0 ? (mean / std) * Math.sqrt(12) : null;
      return { m, w: w.length, l: l.length, win: (w.length / sigs.length) * 100, ret: mean, sharpe };
    }).sort((a, b) => {
      const ma = new Date(`${a.m} 1`), mb = new Date(`${b.m} 1`);
      return ma - mb;
    });

    const tickerBuckets = {};
    for (const s of resolved) {
      const tk = s.ticker || s.tk || "?";
      if (!tickerBuckets[tk]) tickerBuckets[tk] = [];
      tickerBuckets[tk].push(s);
    }
    const tickers = Object.entries(tickerBuckets).map(([tk, sigs]) => {
      const w = sigs.filter((s) => s.outcomePct > 0);
      const mean = sigs.reduce((a, s) => a + s.outcomePct, 0) / sigs.length;
      return { tk, n: sigs.length, win: (w.length / sigs.length) * 100, ret: mean };
    }).sort((a, b) => b.n - a.n);

    return {
      top: [
        { label: "Total signals", value: total.toLocaleString("en-US"), sub: "Resolved positions", tone: "neutral" },
        { label: "Cumulative win rate", value: `${winRate.toFixed(1)}%`, sub: "Closed positions only", tone: winRate >= 55 ? "up" : "down" },
        { label: "Equal-weight return", value: fmtRet(avgReturn), sub: "Paper-traded", tone: avgReturn >= 0 ? "up" : "down" },
        { label: "Max drawdown", value: `−${maxDD.toFixed(1)}%`, sub: "Peak-to-trough", tone: "down" },
      ],
      months: months.map((m) => ({ ...m, ret: fmtRet(m.ret), sharpe: m.sharpe != null ? m.sharpe.toFixed(2) : "—" })),
      tickers: tickers.map((t) => ({ ...t, ret: fmtRet(t.ret) })),
    };
  }, [histSignals]);
}

function PageTrack({ histSignals }) {
  const data = useTrackData(histSignals);
  const top = data?.top || M_TRACK_TOP;
  const months = data?.months || M_TRACK_MONTHS;
  const tickers = data?.tickers || M_TRACK_TICKERS;

  return (
    <div className="page wrap" style={{ paddingTop: 32, paddingBottom: 64 }}>
      <div style={{ textAlign: "center", marginBottom: 28 }}>
        <div className="kicker" style={{ marginBottom: 10, display: "inline-flex", alignItems: "center", gap: 8, padding: "5px 12px", border: "1px solid var(--line)", borderRadius: 999 }}>
          <LiveDot></LiveDot> {data ? "LIVE DATA · NO PII · AGGREGATE ONLY" : "DEMO DATA · NO PII · AGGREGATE ONLY"}
        </div>
        <h2 style={{ fontSize: 30, fontWeight: 650, letterSpacing: "-0.025em", margin: "0 0 8px", textWrap: "balance" }}>Every signal. Audited. No cherry-picking.</h2>
        <p style={{ fontSize: 14, color: "var(--text-dim)", maxWidth: 520, margin: "0 auto", textWrap: "pretty" }}>
          A public ledger of every signal fired since launch — wins, losses, and unresolved positions, updated as each horizon resolves.
        </p>
      </div>

      <div className="track-stats" style={{ marginBottom: 28 }}>
        {top.map((s, i) => <TrackStat key={i} s={s}></TrackStat>)}
      </div>

      <div className="track-two">
        <div className="glass" style={{ padding: 20 }}>
          <div className="kicker" style={{ marginBottom: 16 }}>LAST {Math.min(6, months.length)} MONTHS · WIN RATE</div>
          <MonthBars months={months.slice(-6)}></MonthBars>
          <div style={{ marginTop: 18, overflowX: "auto" }}>
            <table className="mono" style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
              <thead>
                <tr style={{ textAlign: "right", color: "var(--text-faint)" }}>
                  <th style={{ textAlign: "left", padding: "6px 8px", fontWeight: 500 }}>Month</th>
                  <th style={{ padding: "6px 8px", fontWeight: 500 }}>Wins</th>
                  <th style={{ padding: "6px 8px", fontWeight: 500 }}>Losses</th>
                  <th style={{ padding: "6px 8px", fontWeight: 500 }}>Win %</th>
                  <th style={{ padding: "6px 8px", fontWeight: 500 }}>Return</th>
                  <th style={{ padding: "6px 8px", fontWeight: 500 }}>Sharpe</th>
                </tr>
              </thead>
              <tbody>
                {months.slice(-6).map((m, i) => (
                  <tr key={i} style={{ borderTop: "1px solid var(--line-soft)", textAlign: "right" }}>
                    <td style={{ textAlign: "left", padding: "8px", fontWeight: 700 }}>{m.m}</td>
                    <td style={{ padding: "8px", color: "var(--text-dim)" }}>{m.w}</td>
                    <td style={{ padding: "8px", color: "var(--text-dim)" }}>{m.l}</td>
                    <td style={{ padding: "8px" }}>{m.win.toFixed ? m.win.toFixed(1) : m.win}%</td>
                    <td style={{ padding: "8px", color: m.ret && m.ret.startsWith("+") ? "var(--bull)" : m.ret && m.ret.startsWith("−") ? "var(--bear)" : "var(--text)" }}>{m.ret}</td>
                    <td style={{ padding: "8px" }}>{m.sharpe}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="glass" style={{ padding: 20, alignSelf: "start" }}>
          <div className="kicker" style={{ marginBottom: 14 }}>TOP TICKERS BY SIGNAL COUNT</div>
          <div>
            {tickers.map((t, i) => {
              const max = Math.max(...tickers.map((x) => x.n));
              return (
                <div key={i} style={{ padding: "10px 0", borderBottom: "1px solid var(--line-soft)" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
                    <span className="mono" style={{ fontSize: 13, fontWeight: 700, width: 52 }}>{t.tk}</span>
                    <span className="mono dim" style={{ fontSize: 11 }}>{t.n} signals</span>
                    <span className="mono" style={{ fontSize: 11.5, marginLeft: "auto", color: t.win >= 62 ? "var(--bull)" : "var(--neutral)" }}>{t.win.toFixed ? t.win.toFixed(1) : t.win}%</span>
                    <span className="mono bull" style={{ fontSize: 11.5, width: 56, textAlign: "right" }}>{t.ret}</span>
                  </div>
                  <div style={{ height: 3, borderRadius: 2, background: "rgba(255,255,255,0.06)", overflow: "hidden" }}>
                    <div style={{ width: `${(t.n / max) * 100}%`, height: "100%", background: "var(--bull)", opacity: 0.5 }}></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      <div style={{ marginTop: 20, padding: "14px 18px", borderRadius: 8, border: "1px solid var(--line-soft)", background: "rgba(255,255,255,0.012)", fontSize: 11.5, color: "var(--text-faint)", lineHeight: 1.6, textWrap: "pretty" }}>
        <span className="neut" style={{ fontWeight: 700 }}>Not financial advice.</span> These statistics reflect algorithmic signal output — not real-money trades. Past performance does not guarantee future results. All trading involves substantial risk of loss. SIGNAL.TRADE is not a registered investment adviser.
      </div>
    </div>
  );
}

Object.assign(window, { PageTrack });
