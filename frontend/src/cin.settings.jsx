/* global React */
// SIGNAL.TRADE cinematic — Settings.
const { useState: sUseState } = React;

function SettingRow({ label, sub, control }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 16, padding: "14px 0", borderBottom: "1px solid var(--line-soft)" }}>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontSize: 13.5, fontWeight: 500 }}>{label}</div>
        {sub && <div style={{ fontSize: 12, color: "var(--text-faint)", marginTop: 2, lineHeight: 1.5, textWrap: "pretty" }}>{sub}</div>}
      </div>
      {control}
    </div>
  );
}

function Tgl({ on, onChange }) {
  return <button className={`tgl ${on ? "on" : ""}`} onClick={() => onChange(!on)} style={{ cursor: "pointer" }} aria-pressed={on}></button>;
}

const MY_DATA = [
  { what: "Tickers you tap and how long you read each signal", why: "Ranks your watchlist and surfaces similar setups first", kind: "Behavioral" },
  { what: "Signal outcomes you acted on vs. ignored", why: "Calibrates the confidence threshold for your alerts", kind: "Behavioral" },
  { what: "Delivery windows and quiet hours", why: "Times pushes so they never wake you", kind: "Preference" },
  { what: "Paper-trade history", why: "Trains the position-sizing suggestions", kind: "Simulation" },
  { what: "Telegram chat ID and timezone", why: "Routes alerts to the right device, in your local time", kind: "Account" },
];

function PageSettings() {
  const [tab, setTab] = sUseState("data");
  const [s, setS] = sUseState({
    push: true, quiet: true, digest: false, conf: true,
    behav: true, outcomes: true, papertrades: true,
  });
  const set = (k) => (v) => setS((x) => ({ ...x, [k]: v }));
  const tabs = [
    ["data", "My Data"],
    ["alerts", "Alerts"],
    ["account", "Account"],
    ["billing", "Billing"],
  ];
  return (
    <div className="page wrap" style={{ paddingTop: 32, paddingBottom: 64, maxWidth: 880 }}>
      <h2 style={{ fontSize: 26, fontWeight: 650, letterSpacing: "-0.02em", margin: "0 0 4px" }}>Settings</h2>
      <p style={{ fontSize: 13, color: "var(--text-faint)", margin: "0 0 24px" }}>Transparency is trust. Everything the engine knows about you is on this page.</p>
      <div style={{ display: "flex", gap: 4, borderBottom: "1px solid var(--line)", marginBottom: 24 }}>
        {tabs.map(([id, label]) => (
          <button key={id} onClick={() => setTab(id)} style={{
            background: "none", border: "none", padding: "10px 16px",
            fontSize: 13, fontWeight: 600,
            color: tab === id ? "var(--bull)" : "var(--text-dim)",
            borderBottom: tab === id ? "2px solid var(--bull)" : "2px solid transparent",
            marginBottom: -1, transition: "color 0.18s var(--ease)",
          }}>{label}</button>
        ))}
      </div>

      {tab === "data" && (
        <div className="page">
          <div className="glass" style={{ padding: "20px 24px", marginBottom: 16, background: "linear-gradient(135deg, rgba(34,211,238,0.06), rgba(255,255,255,0.015) 60%)" }}>
            <div className="kicker" style={{ color: "var(--bull)", marginBottom: 8 }}>WHAT THE SYSTEM KNOWS — AND WHY</div>
            <p style={{ margin: 0, fontSize: 13, color: "var(--text-dim)", lineHeight: 1.6, textWrap: "pretty" }}>
              The engine personalizes your dashboard using the data below. Every item can be switched off — the product keeps working, just less tailored. Nothing is sold or shared. Ever.
            </p>
          </div>
          {MY_DATA.map((d, i) => (
            <div key={i} className="glass glass-hover" style={{ padding: "16px 20px", marginBottom: 10, display: "grid", gridTemplateColumns: "1fr auto", gap: "4px 16px", alignItems: "center" }}>
              <div>
                <div style={{ fontSize: 13.5, fontWeight: 500, marginBottom: 3 }}>{d.what}</div>
                <div style={{ fontSize: 12, color: "var(--text-faint)", lineHeight: 1.5 }}>
                  <span style={{ color: "var(--bull)" }}>Why:</span> {d.why}
                </div>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <span className="kicker" style={{ border: "1px solid var(--line)", borderRadius: 4, padding: "2px 7px" }}>{d.kind}</span>
                {i < 2 ? <Tgl on={i === 0 ? s.behav : s.outcomes} onChange={set(i === 0 ? "behav" : "outcomes")}></Tgl>
                  : i === 3 ? <Tgl on={s.papertrades} onChange={set("papertrades")}></Tgl>
                  : <span className="kicker" style={{ color: "var(--text-ghost)" }}>REQUIRED</span>}
              </div>
            </div>
          ))}
          <button className="btn sm" style={{ marginTop: 8 }}>Download everything we have on you (.json)</button>
        </div>
      )}

      {tab === "alerts" && (
        <div className="glass page" style={{ padding: "6px 24px 20px" }}>
          <SettingRow label="Telegram push" sub="Instant delivery the moment a signal fires" control={<Tgl on={s.push} onChange={set("push")}></Tgl>}></SettingRow>
          <SettingRow label="Quiet hours" sub="No pushes 22:00–07:00 local — signals queue silently" control={<Tgl on={s.quiet} onChange={set("quiet")}></Tgl>}></SettingRow>
          <SettingRow label="Confidence filter" sub="Only alert above your 70% threshold — suppresses noise" control={<Tgl on={s.conf} onChange={set("conf")}></Tgl>}></SettingRow>
          <SettingRow label="Daily digest" sub="One summary at 08:00 ET instead of real-time pushes" control={<Tgl on={s.digest} onChange={set("digest")}></Tgl>}></SettingRow>
        </div>
      )}

      {tab === "account" && (
        <div className="glass page" style={{ padding: "6px 24px 20px" }}>
          <SettingRow label="Email" control={<span className="mono dim" style={{ fontSize: 12.5 }}>trader@example.com</span>}></SettingRow>
          <SettingRow label="Telegram" control={<span className="mono dim" style={{ fontSize: 12.5 }}>@quietquant · connected</span>}></SettingRow>
          <SettingRow label="Timezone" control={<span className="mono dim" style={{ fontSize: 12.5 }}>America/New_York</span>}></SettingRow>
          <SettingRow label="Two-factor authentication" sub="TOTP app enabled" control={<span className="kicker" style={{ color: "var(--bull)" }}>ON</span>}></SettingRow>
        </div>
      )}

      {tab === "billing" && (
        <div className="glass page" style={{ padding: "6px 24px 20px" }}>
          <SettingRow label="Plan" sub="Pro · unlimited signals, backtests, paper trading" control={<span className="mono" style={{ fontSize: 13, fontWeight: 700, color: "var(--bull)" }}>$49/mo</span>}></SettingRow>
          <SettingRow label="Next invoice" control={<span className="mono dim" style={{ fontSize: 12.5 }}>Jul 1, 2026</span>}></SettingRow>
          <SettingRow label="Payment method" control={<span className="mono dim" style={{ fontSize: 12.5 }}>•••• 4242</span>}></SettingRow>
          <SettingRow label="Cancel anytime" sub="One click via Stripe portal — no questions, runs to period end" control={<button className="btn sm">Manage</button>}></SettingRow>
        </div>
      )}
    </div>
  );
}

Object.assign(window, { PageSettings });
