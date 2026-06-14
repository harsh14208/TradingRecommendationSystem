/* global React */
// SIGNAL.TRADE cinematic — Track Record page (real audited stats).

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

function MonthBars() {
  const ms = [...M_TRACK_MONTHS].reverse();
  const max = Math.max(...ms.map((m) => m.win));
  return (
    <div style={{ display: "flex", alignItems: "flex-end", gap: 10, height: 110, padding: "0 4px" }}>
      {ms.map((m, i) => {
        const h = (m.win / max) * 100;
        const col = m.win >= 62 ? "var(--bull)" : "var(--neutral)";
        return (
          <div key={i} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: 6 }}>
            <span className="mono" style={{ fontSize: 10.5, fontWeight: 600, color: col }}>{m.win}%</span>
            <div style={{ width: "100%", height: `${h}%`, minHeight: 4, borderRadius: "3px 3px 0 0", background: `linear-gradient(180deg, ${col}, rgba(255,255,255,0.04))` }}></div>
            <span className="mono" style={{ fontSize: 9.5, color: "var(--text-faint)" }}>{m.m.split(" ")[0]}</span>
          </div>
        );
      })}
    </div>
  );
}

function PageTrack() {
  return (
    <div className="page wrap" style={{ paddingTop: 32, paddingBottom: 64 }}>
      <div style={{ textAlign: "center", marginBottom: 28 }}>
        <div className="kicker" style={{ marginBottom: 10, display: "inline-flex", alignItems: "center", gap: 8, padding: "5px 12px", border: "1px solid var(--line)", borderRadius: 999 }}>
          <LiveDot></LiveDot> LIVE DATA · NO PII · AGGREGATE ONLY
        </div>
        <h2 style={{ fontSize: 30, fontWeight: 650, letterSpacing: "-0.025em", margin: "0 0 8px", textWrap: "balance" }}>Every signal. Audited. No cherry-picking.</h2>
        <p style={{ fontSize: 14, color: "var(--text-dim)", maxWidth: 520, margin: "0 auto", textWrap: "pretty" }}>
          A public ledger of every signal fired since launch — wins, losses, and unresolved positions, updated as each horizon resolves.
        </p>
      </div>

      <div className="track-stats" style={{ marginBottom: 28 }}>
        {M_TRACK_TOP.map((s, i) => <TrackStat key={i} s={s}></TrackStat>)}
      </div>

      <div className="track-two">
        <div className="glass" style={{ padding: 20 }}>
          <div className="kicker" style={{ marginBottom: 16 }}>LAST 6 MONTHS · WIN RATE</div>
          <MonthBars></MonthBars>
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
                {M_TRACK_MONTHS.map((m, i) => (
                  <tr key={i} style={{ borderTop: "1px solid var(--line-soft)", textAlign: "right" }}>
                    <td style={{ textAlign: "left", padding: "8px", fontWeight: 700 }}>{m.m}</td>
                    <td style={{ padding: "8px", color: "var(--text-dim)" }}>{m.w}</td>
                    <td style={{ padding: "8px", color: "var(--text-dim)" }}>{m.l}</td>
                    <td style={{ padding: "8px" }}>{m.win}%</td>
                    <td style={{ padding: "8px", color: "var(--bull)" }}>{m.ret}</td>
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
            {M_TRACK_TICKERS.map((t, i) => {
              const max = Math.max(...M_TRACK_TICKERS.map((x) => x.n));
              return (
                <div key={i} style={{ padding: "10px 0", borderBottom: "1px solid var(--line-soft)" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
                    <span className="mono" style={{ fontSize: 13, fontWeight: 700, width: 52 }}>{t.tk}</span>
                    <span className="mono dim" style={{ fontSize: 11 }}>{t.n} signals</span>
                    <span className="mono" style={{ fontSize: 11.5, marginLeft: "auto", color: t.win >= 62 ? "var(--bull)" : "var(--neutral)" }}>{t.win}%</span>
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
