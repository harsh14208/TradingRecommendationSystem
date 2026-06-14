/* global React */
// SIGNAL.TRADE cinematic — market context data, ported from src/data.jsx + data.js (previous designs).

const M_FEAR_GREED = { score: 42.7, label: "Fear", prev_close: 45.1, prev_1w: 38.2, prev_1m: 61.0 };

const M_MACRO = {
  vix: 18.4, vix3m: 20.1, yield_10y: 4.32, yield_2y: 4.91, yc_spread: -0.59,
  dxy_1m: 1.2, spx_vs_50d: 2.3, spx_vs_200d: 8.1, cpi: 3.4, fed_rate: 5.25,
  macro_score: 12, sector_rotation: "early_bull",
  vix_5d: [21.2, 20.4, 19.6, 19.1, 18.4],
};

const M_BREADTH = { pct_above_50d: 58.3, pct_above_200d: 64.1, signal: "bullish", score: 5 };
const M_PUTCALL = { ratio: 0.82, signal: "neutral", score: 0 };
const M_NAAIM   = { bull_pct: 72.3, bear_pct: 27.7, spread: 44.6, signal: "bearish", score: -4 };
const M_COT     = { lev_long: 124500, lev_short: 198300, net_contracts: -73800, net_pct: -37.1, signal: "bullish", score: 5 };
const M_HMM     = { regime: "bull", bull_prob: 0.73, bear_prob: 0.27, transition_risk: 0.18, vix_z: -0.4 };

const M_CONTEXT_SIGNALS = [
  { src: "VIX",      head: "VIX low (calm)",        body: "VIX at 18.4 is below its 1-year mean. Low realized vol historically supports continued upside, though it also marks late-cycle complacency.", sentiment: "bullish" },
  { src: "Yield",    head: "Yield curve inverted",  body: "10Y minus 2Y is −0.59%. Persistent inversion has preceded recessions historically, but the signal can lead by 6–18 months.", sentiment: "bearish" },
  { src: "Breadth",  head: "Breadth healthy",       body: "64.1% of S&P 500 names trade above their 200-day moving average — participation is broad rather than concentrated.", sentiment: "bullish" },
  { src: "COT",      head: "Hedge funds net short", body: "Leveraged funds are net short −37.1% of total contracts. Crowded short positioning is a contrarian bullish setup if price reclaims trend.", sentiment: "bullish" },
  { src: "NAAIM",    head: "Managers over-exposed", body: "Active managers report 72.3% equity exposure — in the historically over-invested zone. Contrarian read is cautious near term.", sentiment: "bearish" },
  { src: "DXY",      head: "Dollar firming",        body: "DXY is +1.2% over the trailing month. A rising dollar typically tightens financial conditions and weighs on multinational earnings.", sentiment: "bearish" },
  { src: "Breadth",  head: "SPX above 50d & 200d",  body: "Index is +2.3% above its 50-day and +8.1% above its 200-day average — trend is intact across both timeframes.", sentiment: "bullish" },
  { src: "Put/Call", head: "Options neutral",       body: "Equity put/call at 0.82 — neither greedy nor fearful. No contrarian edge from options flow at the moment.", sentiment: "neutral" },
];

const M_SECTORS = [
  { etf: "XLK",  name: "Technology",        weight: 29.4, ret_1d:  0.82, ret_1w:  2.10, ret_1m:  4.30, ret_3m:  8.10, ret_ytd: 12.40, flow_1w:  420.5, flow_1m: -120.3 },
  { etf: "XLV",  name: "Health Care",       weight: 13.1, ret_1d:  0.31, ret_1w:  0.40, ret_1m:  1.10, ret_3m:  2.80, ret_ytd:  4.20, flow_1w:   65.0, flow_1m:  140.5 },
  { etf: "XLF",  name: "Financials",        weight: 12.9, ret_1d: -0.31, ret_1w:  0.80, ret_1m:  1.20, ret_3m:  3.40, ret_ytd:  6.80, flow_1w:   88.1, flow_1m:  310.0 },
  { etf: "XLC",  name: "Communication",     weight:  8.7, ret_1d:  0.15, ret_1w: -0.30, ret_1m: -0.80, ret_3m:  2.10, ret_ytd:  5.40, flow_1w:  -28.4, flow_1m:  -45.0 },
  { etf: "XLY",  name: "Consumer Discret.", weight:  9.1, ret_1d:  0.42, ret_1w:  1.20, ret_1m:  2.40, ret_3m:  4.90, ret_ytd:  7.10, flow_1w:  152.3, flow_1m:  205.6 },
  { etf: "XLI",  name: "Industrials",       weight:  8.5, ret_1d:  0.18, ret_1w:  0.50, ret_1m:  0.50, ret_3m:  1.80, ret_ytd:  3.40, flow_1w:   12.0, flow_1m:   55.0 },
  { etf: "XLP",  name: "Consumer Staples",  weight:  6.0, ret_1d: -0.12, ret_1w: -0.40, ret_1m: -0.30, ret_3m: -0.90, ret_ytd:  0.40, flow_1w:  -64.5, flow_1m: -110.0 },
  { etf: "XLE",  name: "Energy",            weight:  4.2, ret_1d:  1.20, ret_1w: -1.40, ret_1m: -2.10, ret_3m: -5.20, ret_ytd: -3.10, flow_1w:  -38.2, flow_1m: -210.4 },
  { etf: "XLB",  name: "Materials",         weight:  2.4, ret_1d:  0.20, ret_1w: -0.20, ret_1m: -1.10, ret_3m: -2.30, ret_ytd: -0.80, flow_1w:  -10.5, flow_1m:  -22.0 },
  { etf: "XLRE", name: "Real Estate",       weight:  2.4, ret_1d: -0.45, ret_1w: -1.10, ret_1m: -1.80, ret_3m: -3.40, ret_ytd: -2.20, flow_1w:  -22.0, flow_1m:  -88.0 },
  { etf: "XLU",  name: "Utilities",         weight:  2.4, ret_1d:  0.04, ret_1w:  0.10, ret_1m:  0.30, ret_3m:  0.80, ret_ytd:  1.60, flow_1w:   18.4, flow_1m:   40.2 },
];

const M_ROTATION = [
  { id: "early_bull", label: "Early Bull", etfs: ["XLY", "XLK", "XLF"],  note: "Cyclicals lead off the bottom" },
  { id: "late_bull",  label: "Late Bull",  etfs: ["XLE", "XLB", "XLI"],  note: "Inflationary, capex-heavy names" },
  { id: "early_bear", label: "Early Bear", etfs: ["XLV", "XLP", "XLRE"], note: "Defensives outperform first" },
  { id: "late_bear",  label: "Late Bear",  etfs: ["XLU", "XLP"],         note: "Bond proxies, yield-sensitive" },
];

const M_CALENDAR = [
  { date: "2026-05-19", time: "08:30", name: "Retail Sales (MoM)",         label: "Retail",  impact: "MEDIUM", category: "growth",     forecast: "0.3%",  previous: "0.4%",  description: "Month-over-month change in retail sales — consumer spending pulse." },
  { date: "2026-05-21", time: "08:30", name: "Consumer Price Index (YoY)", label: "CPI",     impact: "HIGH",   category: "inflation",  forecast: "3.2%",  previous: "3.5%",  description: "Headline inflation. Higher than expected → bearish equities, bullish USD, bearish bonds." },
  { date: "2026-05-21", time: "08:30", name: "Producer Price Index (YoY)", label: "PPI",     impact: "MEDIUM", category: "inflation",  forecast: "2.4%",  previous: "2.6%",  description: "Wholesale price pressure. Leading indicator for downstream CPI." },
  { date: "2026-05-22", time: "08:30", name: "Initial Jobless Claims",     label: "Jobless", impact: "MEDIUM", category: "employment", forecast: "218K",  previous: "222K",  description: "Weekly labor market read. Sharp rise signals deterioration." },
  { date: "2026-05-23", time: "08:30", name: "GDP (Final, QoQ)",           label: "GDP",     impact: "HIGH",   category: "growth",     forecast: "2.1%",  previous: "2.4%",  description: "Final estimate of last-quarter growth. Above consensus → risk-on; miss → risk-off." },
  { date: "2026-05-26", time: "10:00", name: "Consumer Confidence",        label: "Confid.", impact: "MEDIUM", category: "surveys",    forecast: "102.0", previous: "104.7", description: "Conference Board sentiment. Drives discretionary stock expectations." },
  { date: "2026-05-28", time: "08:30", name: "PCE Price Index (YoY)",      label: "PCE",     impact: "HIGH",   category: "inflation",  forecast: "2.6%",  previous: "2.7%",  description: "Fed's preferred inflation gauge. Drives rate-path repricing." },
  { date: "2026-06-05", time: "08:30", name: "Non-Farm Payrolls",          label: "NFP",     impact: "HIGH",   category: "employment", forecast: "175K",  previous: "192K",  description: "Stronger jobs → hawkish Fed fears, rate-sensitive sectors sell off." },
  { date: "2026-06-10", time: "08:30", name: "Consumer Price Index (YoY)", label: "CPI",     impact: "HIGH",   category: "inflation",  forecast: "3.0%",  previous: "3.2%",  description: "Headline inflation. Higher than expected → bearish equities, bullish USD." },
  { date: "2026-06-17", time: "14:00", name: "FOMC Rate Decision",         label: "FOMC",    impact: "HIGH",   category: "fed",        forecast: "5.25%", previous: "5.25%", description: "Rate decision and dot plot. Volatility spike likely." },
  { date: "2026-06-17", time: "08:30", name: "Producer Price Index",       label: "PPI",     impact: "MEDIUM", category: "inflation",  forecast: "2.3%",  previous: "2.4%",  description: "Wholesale prices ahead of CPI." },
  { date: "2026-06-25", time: "10:00", name: "New Home Sales",             label: "Housing", impact: "LOW",    category: "housing",    forecast: "640K",  previous: "634K",  description: "Rate-sensitive housing demand." },
];

const M_SOURCES = [
  { id: "yahoo", name: "Yahoo Finance", abbr: "YAHO", desc: "Quotes, fundamentals, news",       on: true,  reqs: 1842, latency: 210, feed: "Quotes · 15m" },
  { id: "av",    name: "Alpha Vantage", abbr: "AV",   desc: "Technicals, TA indicators",        on: true,  reqs: 541,  latency: 430, feed: "5/min free tier" },
  { id: "finn",  name: "Finnhub",       abbr: "FINN", desc: "Realtime news, insider",           on: true,  reqs: 2204, latency: 180, feed: "60/min free" },
  { id: "reut",  name: "Reuters / BBG", abbr: "REUT", desc: "RSS newswire",                     on: true,  reqs: 88,   latency: 95,  feed: "Polling 30s" },
  { id: "edgar", name: "SEC EDGAR",     abbr: "EDGR", desc: "8-K, 10-Q, Form 4",                on: true,  reqs: 34,   latency: 620, feed: "Polling 60s" },
  { id: "x",     name: "Twitter / X",   abbr: "X",    desc: "Curated accounts list (42)",       on: true,  reqs: 3102, latency: 330, feed: "Streaming" },
  { id: "redd",  name: "Reddit / WSB",  abbr: "REDD", desc: "r/wallstreetbets sentiment",       on: true,  reqs: 412,  latency: 280, feed: "Polling 5m" },
  { id: "gnews", name: "Google News",   abbr: "GNEW", desc: "Financial category RSS",           on: false, reqs: 0,    latency: 0,   feed: "Disabled" },
  { id: "cal",   name: "Earnings Cal.", abbr: "CAL",  desc: "Upcoming events + estimates",      on: true,  reqs: 22,   latency: 140, feed: "Daily 05:00 ET" },
];

const M_LOG = [
  { t: "09:31:24", s: "sent",  m: "→ BUY NVDA @ 1248.32 (Conf 87%)" },
  { t: "09:14:09", s: "sent",  m: "→ SELL TSLA @ 164.82 (Conf 72%)" },
  { t: "09:02:56", s: "sent",  m: "→ HOLD AAPL — earnings wait" },
  { t: "08:58:44", s: "sent",  m: "→ BUY AMD @ 162.44 (Conf 69%)" },
  { t: "08:42:11", s: "sent",  m: "→ BUY META @ 512.88 (Conf 64%)" },
  { t: "08:31:28", s: "sent",  m: "→ SELL SMCI @ 892.11 (Conf 81%)" },
  { t: "08:12:04", s: "queue", m: "~ HOLD MSFT suppressed (below threshold)" },
  { t: "07:58:20", s: "sent",  m: "→ BUY PLTR @ 23.88 (Conf 61%)" },
  { t: "07:41:11", s: "fail",  m: "✗ Telegram rate limit — retry 30s" },
  { t: "07:30:00", s: "sent",  m: "→ Pre-market scan: 2,847 tickers" },
];

const M_FAQS = [
  { q: "Is this financial advice?", a: "No. Every signal is published with a full disclaimer — for educational and informational purposes only. Past performance does not predict future results. Trade at your own risk; consult a licensed advisor." },
  { q: "How fresh is the data?", a: "Live IEX prices via Alpaca WebSocket. News + options scan every cycle. SEC 13F filings cached 6 hours. Free tier rate-limits respected." },
  { q: "Can I cancel anytime?", a: "Yes. Stripe Billing Portal — one click, no questions. Service runs through end of billing period." },
  { q: "Why Telegram, not WhatsApp?", a: "Telegram has a free, robust Bot API. WhatsApp Business is paywalled per message and harder to self-host. Same instant push, lighter infrastructure." },
  { q: "Do I need to babysit the alerts?", a: "No. Set delivery window (e.g. 09:30–16:00 ET) + active days. Confidence threshold suppresses noise. Quiet hours block off-hours sends." },
  { q: "What about backtesting?", a: "Win rate, Sharpe, max drawdown, Calmar by horizon (1d/3d/7d/14d). Per-ticker track record + auditable simulation. Bayesian smoothing as signals resolve." },
];

// ---- Track record (site.jsx TrackPage) ----
const M_TRACK_TOP = [
  { label: "Total signals", value: "2,194", sub: "Since Jul 2025" },
  { label: "Cumulative win rate", value: "61.4%", sub: "Closed positions only", tone: "up" },
  { label: "Equal-weight return", value: "+38.4%", sub: "Paper-traded", tone: "up" },
  { label: "Max drawdown", value: "−7.2%", sub: "Aug 14, 2025", tone: "down" },
];
const M_TRACK_MONTHS = [
  { m: "Apr 26", w: 142, l: 78, win: 64.5, ret: "+4.8%", sharpe: 1.92 },
  { m: "Mar 26", w: 158, l: 96, win: 62.2, ret: "+6.1%", sharpe: 1.85 },
  { m: "Feb 26", w: 134, l: 88, win: 60.4, ret: "+3.2%", sharpe: 1.62 },
  { m: "Jan 26", w: 167, l: 105, win: 61.4, ret: "+5.7%", sharpe: 1.78 },
  { m: "Dec 25", w: 123, l: 82, win: 60.0, ret: "+2.1%", sharpe: 1.45 },
  { m: "Nov 25", w: 145, l: 91, win: 61.4, ret: "+4.3%", sharpe: 1.71 },
];
const M_TRACK_TICKERS = [
  { tk: "NVDA", n: 84, win: 71.4, ret: "+18.2%" },
  { tk: "PLTR", n: 38, win: 65.8, ret: "+22.1%" },
  { tk: "MSFT", n: 53, win: 64.2, ret: "+7.1%" },
  { tk: "AMD", n: 58, win: 60.3, ret: "+11.4%" },
  { tk: "META", n: 47, win: 59.6, ret: "+8.7%" },
  { tk: "GOOGL", n: 41, win: 58.5, ret: "+5.2%" },
  { tk: "AAPL", n: 62, win: 58.1, ret: "+6.4%" },
  { tk: "TSLA", n: 71, win: 56.3, ret: "+9.8%" },
];

// ---- Pricing (site.jsx Pricing) ----
const M_PRICING = [
  { name: "Free", amt: "$0", per: "forever", desc: "Read-only access. See signals after they fire. No notifications.",
    feats: [["Live signal feed", true], ["Track record + history", true], ["Sector heatmap", true], ["Telegram delivery", false], ["Backtesting", false], ["Paper trading", false]] },
  { name: "Basic", amt: "$9.99", per: "/mo", featured: true, desc: "The full alerting experience — Telegram delivery plus the backtest engine.",
    feats: [["Everything in Free", true], ["Telegram alerts (multi-style)", true], ["Delivery window + active days", true], ["Backtesting (1d/3d/7d/14d)", true], ["Watchlist + price alerts", true], ["PWA mobile app", true]] },
  { name: "Pro", amt: "$19.99", per: "/mo", desc: "Full quant desk: paper trading, correlation matrix, priority delivery.",
    feats: [["Everything in Basic", true], ["Alpaca paper-trade auto-execute", true], ["Signal correlation matrix", true], ["Bayesian confidence intervals", true], ["Portfolio risk dashboard", true], ["Priority queue + API access", true]] },
];

Object.assign(window, {
  M_FEAR_GREED, M_MACRO, M_BREADTH, M_PUTCALL, M_NAAIM, M_COT, M_HMM,
  M_CONTEXT_SIGNALS, M_SECTORS, M_ROTATION, M_CALENDAR, M_SOURCES, M_LOG, M_FAQS,
  M_TRACK_TOP, M_TRACK_MONTHS, M_TRACK_TICKERS, M_PRICING,
});
