// Track-record renderer — external (not inline) to satisfy CSP script-src 'self'.
// Fetches /api/public/track-record and renders aggregate signal performance.
const fmt = (v, d=2) => v == null ? '—' : v.toFixed(d);
const pctFmt = v => v == null ? '—' : (v >= 0 ? '+' : '') + fmt(v) + '%';
const wrColor = v => v == null ? '#8b949e' : v >= 60 ? '#10b981' : v >= 45 ? '#f59e0b' : '#ef4444';
const retColor = v => v == null ? '#8b949e' : v >= 0 ? '#10b981' : '#ef4444';
const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

function setMessage(text) {
  const el = document.getElementById('content');
  el.textContent = '';
  const div = document.createElement('div');
  div.className = 'spinner';
  div.textContent = text;
  el.appendChild(div);
}

async function load() {
  try {
    const res = await fetch('/api/public/track-record');
    const d   = await res.json();
    if (d.no_data) {
      setMessage('No resolved signals yet — check back after the first week of trading.');
      return;
    }
    render(d);
  } catch(e) {
    setMessage('Could not load data — try refreshing.');
  }
}

function render(d) {
  const o = d.overall || {};
  const html = `
    <section>
      <div class="section-title">Overall performance · ${esc(d.total_signals)} resolved signals</div>
      <div class="grid grid-4">
        ${card('Win Rate', o.win_rate != null ? o.win_rate.toFixed(1)+'%' : '—', wrColor(o.win_rate), o.n ? o.n+' signals' : '')}
        ${card('Avg Return', pctFmt(o.avg_return), retColor(o.avg_return), 'per signal')}
        ${card('Avg Win', pctFmt(o.avg_win), '#10b981', 'winning trades')}
        ${card('Sharpe Ratio', o.sharpe != null ? fmt(o.sharpe) : '—', o.sharpe >= 1 ? '#10b981' : o.sharpe >= 0 ? '#f59e0b' : '#ef4444', 'annualised')}
      </div>
    </section>

    ${d.by_month?.length > 1 ? `
    <section>
      <div class="section-title">Win rate by month</div>
      <div class="card">
        <div class="month-bar">
          ${d.by_month.map(m => {
            const wr = m.win_rate ?? 0;
            const c  = wrColor(wr);
            return `<div class="month-col">
              <div class="pct" style="color:${c}">${wr.toFixed(0)}%</div>
              <div class="rect" style="background:${c};height:${Math.max(4,wr*0.6)}px"></div>
              <div class="lbl">${esc(m.month.slice(5))}</div>
            </div>`;
          }).join('')}
        </div>
        <div style="display:grid;grid-template-columns:repeat(${d.by_month.length},1fr);gap:6px;margin-top:12px">
          ${d.by_month.map(m => `
            <div style="text-align:center;font-size:10px;font-family:monospace;color:${retColor(m.avg_return)}">${pctFmt(m.avg_return)}<br><span style="color:#8b949e">${m.n} sigs</span></div>
          `).join('')}
        </div>
      </div>
    </section>` : ''}

    ${d.by_action?.length ? `
    <section>
      <div class="section-title">By signal direction</div>
      <div class="card">
        <div class="table-wrap">
        <table>
          <tr><th>Direction</th><th>Signals</th><th>Win Rate</th><th>Avg Return</th><th>Avg Win</th><th>Avg Loss</th></tr>
          ${d.by_action.map(a => `<tr>
            <td><span class="action-pill ${esc(a.action)}">${esc(a.action)}</span></td>
            <td style="text-align:right">${esc(a.n)}</td>
            <td style="text-align:right;color:${wrColor(a.win_rate)};font-weight:700">${a.win_rate != null ? a.win_rate.toFixed(1)+'%' : '—'}</td>
            <td style="text-align:right;color:${retColor(a.avg_return)}">${pctFmt(a.avg_return)}</td>
            <td style="text-align:right;color:#10b981">${pctFmt(a.avg_win)}</td>
            <td style="text-align:right;color:#ef4444">${pctFmt(a.avg_loss)}</td>
          </tr>`).join('')}
        </table>
        </div>
      </div>
    </section>` : ''}

    ${d.top_tickers?.length ? `
    <section>
      <div class="section-title">Performance by ticker</div>
      <div class="card">
        <div class="table-wrap">
        <table>
          <tr><th>Ticker</th><th>Signals</th><th>Win Rate</th><th>Avg Return</th><th>Sharpe</th></tr>
          ${d.top_tickers.map(t => `<tr>
            <td>${esc(t.ticker)}</td>
            <td style="text-align:right">${esc(t.n)}</td>
            <td style="text-align:right;color:${wrColor(t.win_rate)};font-weight:700">${t.win_rate != null ? t.win_rate.toFixed(1)+'%' : '—'}</td>
            <td style="text-align:right;color:${retColor(t.avg_return)}">${pctFmt(t.avg_return)}</td>
            <td style="text-align:right;color:${t.sharpe >= 1 ? '#10b981' : t.sharpe >= 0 ? '#f59e0b' : '#8b949e'}">${t.sharpe != null ? fmt(t.sharpe) : '—'}</td>
          </tr>`).join('')}
        </table>
        </div>
      </div>
    </section>` : ''}

    <div class="grid grid-2">
      ${d.top_signals?.length ? `
      <section>
        <div class="section-title">Best signals</div>
        <div style="display:flex;flex-direction:column;gap:8px">
          ${d.top_signals.map(s => `
            <div class="signal-card">
              <div style="display:flex;justify-content:space-between;align-items:center">
                <span class="ticker">${esc(s.ticker)}</span>
                <span class="action-pill ${esc(s.action)}">${esc(s.action)}</span>
              </div>
              <div class="ret up">+${fmt(s.return_pct)}%</div>
              <div style="font-size:11px;color:#8b949e">${esc(s.date)} · ${esc(s.confidence.toFixed(0))}% conf</div>
            </div>`).join('')}
        </div>
      </section>` : ''}

      ${d.worst_signals?.length ? `
      <section>
        <div class="section-title">Worst signals</div>
        <div style="display:flex;flex-direction:column;gap:8px">
          ${d.worst_signals.map(s => `
            <div class="signal-card">
              <div style="display:flex;justify-content:space-between;align-items:center">
                <span class="ticker">${esc(s.ticker)}</span>
                <span class="action-pill ${esc(s.action)}">${esc(s.action)}</span>
              </div>
              <div class="ret down">${fmt(s.return_pct)}%</div>
              <div style="font-size:11px;color:#8b949e">${esc(s.date)} · ${esc(s.confidence.toFixed(0))}% conf</div>
            </div>`).join('')}
        </div>
      </section>` : ''}
    </div>
  `;
  document.getElementById('content').innerHTML = html;
}

function card(label, value, color, sub) {
  return `<div class="card">
    <div class="card-label">${label}</div>
    <div class="card-value" style="color:${color||'#e6edf3'}">${value}</div>
    ${sub ? `<div class="card-sub">${sub}</div>` : ''}
  </div>`;
}

load();
