/* global React */
// SIGNAL.TRADE cinematic — Tools hub. Reuses the legacy modal/view components
// (AccountModal, WatchlistView, AlertsView, ScreenerView, PaperView, etc.)
// so advanced features stay reachable from the new shell.

function ToolCard({ title, desc, onClick }) {
  return (
    <button className="glass glass-hover" onClick={onClick} style={{
      padding: "20px 22px", textAlign: "left", display: "flex", flexDirection: "column", gap: 8,
      background: "var(--panel)", border: "1px solid var(--line-soft)", borderRadius: 10,
      color: "var(--text)", cursor: "pointer",
    }}>
      <div style={{ fontSize: 15, fontWeight: 600 }}>{title}</div>
      <div style={{ fontSize: 12.5, color: "var(--text-dim)", lineHeight: 1.5, textWrap: "pretty" }}>{desc}</div>
      <span className="kicker" style={{ marginTop: "auto", color: "var(--bull)" }}>OPEN →</span>
    </button>
  );
}

function PageTools({ openAccount, openWatchlist, openAlerts, openScreener, openMarket, openSector, openCalendar,
  openHistory, openRules, openPerformance, openPricing, openTweaks, currentUser }) {
  return (
    <div className="page wrap" style={{ paddingTop: 32, paddingBottom: 64 }}>
      <div style={{ display: "flex", alignItems: "baseline", gap: 12, marginBottom: 22, flexWrap: "wrap" }}>
        <h2 style={{ fontSize: 26, fontWeight: 650, letterSpacing: "-0.02em", margin: 0 }}>Tools</h2>
        <span className="kicker">ADVANCED FEATURES</span>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))", gap: 14 }}>
        <ToolCard title="Account" desc="Telegram link, billing, broker connect, auto-execution, referral." onClick={openAccount} />
        <ToolCard title="Watchlist" desc="Tickers you follow, price alerts, and related signals." onClick={openWatchlist} />
        <ToolCard title="Alerts" desc="Create and manage signal alert rules." onClick={openAlerts} />
        <ToolCard title="Screener" desc="Build custom screens and save screen presets." onClick={openScreener} />
        <ToolCard title="Market Overview" desc="Breadth, volatility, and macro snapshot." onClick={openMarket} />
        <ToolCard title="Sector Heatmap" desc="Sector rotation, relative strength, and ETF flows." onClick={openSector} />
        <ToolCard title="Earnings Calendar" desc="Upcoming earnings and macro events." onClick={openCalendar} />
        <ToolCard title="Signal History" desc="Archived signals, filters, and CSV export." onClick={openHistory} />
        <ToolCard title="Rules & Filters" desc="Trading style, confidence, delivery window, and earnings block." onClick={openRules} />
        <ToolCard title="My Performance" desc="Delivered signals, win rate, and recent exits." onClick={openPerformance} />
        <ToolCard title="Tweaks" desc="Theme, density, aggressiveness, and engine weight overrides." onClick={openTweaks} />
        <ToolCard title="Pricing" desc="View plans and upgrade or manage billing." onClick={openPricing} />
      </div>
    </div>
  );
}

Object.assign(window, { PageTools });
