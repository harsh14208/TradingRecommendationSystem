/* global React */
// SIGNAL.TRADE cinematic — data layer. REAL product data (ported from data.js / site.jsx),
// plus deterministic chart synthesis (seeded PRNG) for the price/spark visuals.

function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a |= 0; a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
function genSeries(seed, n, start, drift, vol) {
  const rnd = mulberry32(seed);
  const out = [start];
  for (let i = 1; i < n; i++) {
    const shock = (rnd() - 0.5) * 2 * vol;
    out.push(Math.max(1, out[i - 1] * (1 + drift + shock)));
  }
  return out;
}

// ---- REAL signals (data.js) enriched with chart params + historical win rate ----
const SIGNALS = [
  {
    tk: "NVDA", name: "NVIDIA Corporation", signal: "BUY", conf: 87, px: 1248.32, chgPct: +0.23,
    rr: 3.4, entry: 1245, stop: 1188, target: 1385, mcap: "3.06T", vol: "38.2M", pe: 62.1, ts: "09:31:22",
    style: "swing", win: 71, sources: ["FINN", "X", "REUT"],
    headline: "Breakout above the 200-DMA with a fresh licensing catalyst.",
    narrative: "NVDA cleared its 200-day average on 1.4× volume the same morning Reuters reported expanded CUDA licensing. Technicals, options flow and retail sentiment all line up on the long side — the rare four-source agreement.",
    rationale: [
      { src: "REUT", head: "Reuters: NVIDIA expands CUDA licensing to 3 new hyperscalers", meta: "Reuters · 2m ago", sentiment: "pos", body: "Unconfirmed sourcing from 2 senior exec quotes; stock moved +1.8% intraday." },
      { src: "TECH", head: "Daily MACD crossover + RSI rebound from 42", meta: "Alpha Vantage · computed", sentiment: "pos", body: "50-DMA crossed above 200-DMA on 4/17; volume 1.4× the 20-day average." },
      { src: "X", head: "Unusual options flow — 14k calls at $1,300 strike", meta: "Twitter/X · 14 accounts tracked", sentiment: "pos", body: "Flow detected across @unusual_whales plus 3 verified prop traders." },
      { src: "REDD", head: "r/wallstreetbets sentiment +62% WoW", meta: "Reddit · rolling 48h", sentiment: "neu", body: "Mentions up 340 → 551; bullish/bearish ratio 3.1 (was 1.8 last week)." },
    ],
    seed: 11, drift: 0.0026, vol: 0.022,
  },
  {
    tk: "TSLA", name: "Tesla, Inc.", signal: "SELL", conf: 72, px: 164.82, chgPct: -2.43,
    rr: 2.1, entry: 164.5, stop: 172.0, target: 148.0, mcap: "524B", vol: "102.4M", pe: 41.3, ts: "09:14:08",
    style: "intraday", win: 56, sources: ["EDGAR", "YAHOO", "X"],
    headline: "Delivery miss plus a material 8-K — distribution underway.",
    narrative: "A 10.5% YoY delivery decline — the first since 2020 — landed alongside a $412M warranty reserve filing. Price broke its 50-day on expanding volume. Bearish until $172 is reclaimed.",
    rationale: [
      { src: "EDGR", head: "SEC 8-K: $412M warranty reserve adjustment", meta: "EDGAR · filed 04:30 ET", sentiment: "neg", body: "Material filing; cash impact spread across Q2–Q4." },
      { src: "YAHO", head: "Q1 deliveries 386.8k vs est. 432k", meta: "Yahoo Finance · 06:00 ET", sentiment: "neg", body: "−10.5% YoY; first year-over-year decline since 2020." },
      { src: "TECH", head: "Breakdown below 50-DMA, next support $152", meta: "Alpha Vantage · computed", sentiment: "neg", body: "MACD bearish cross on 4/16; volume expanding into the move." },
    ],
    seed: 13, drift: -0.0019, vol: 0.030,
  },
  {
    tk: "SMCI", name: "Super Micro Computer", signal: "SELL", conf: 81, px: 892.11, chgPct: -3.08,
    rr: 2.9, entry: 890, stop: 948, target: 760, mcap: "52B", vol: "8.1M", pe: 44.2, ts: "08:31:27",
    style: "intraday", win: 64, sources: ["X", "REDD"],
    headline: "Short thesis going viral as margin concerns propagate.",
    narrative: "A Hindenburg-style thread crossed 840k views questioning the AI-server backlog. IR offered only a partial rebuttal. Momentum and sentiment both rolled over hard.",
    rationale: [
      { src: "X", head: "Hindenburg-style thread gaining traction (840k views)", meta: "Twitter/X", sentiment: "neg", body: "Claims overstated AI-server backlog; partial refute from IR." },
      { src: "TECH", head: "Lost $920 pivot on 2.1× volume", meta: "Alpha Vantage · computed", sentiment: "neg", body: "Failed retest of prior support; next shelf near $760." },
    ],
    seed: 19, drift: -0.0024, vol: 0.040,
  },
  {
    tk: "AMD", name: "Advanced Micro Devices", signal: "BUY", conf: 69, px: 162.44, chgPct: +2.02,
    rr: 2.8, entry: 160, stop: 148, target: 188, mcap: "263B", vol: "61.9M", pe: 232.0, ts: "08:58:41",
    style: "swing", win: 60, sources: ["REUT", "FINN"],
    headline: "MI400 roadmap leak expands the accelerator TAM.",
    narrative: "Bloomberg reports the MI400 tapes out in Q3 with a 2.3× perf-per-watt claim, sourced from three Taiwan supply-chain partners. Price reclaimed its 50-day on the news.",
    rationale: [
      { src: "REUT", head: "Bloomberg: MI400 tapes out Q3; 2.3× perf/watt claim", meta: "Bloomberg RSS", sentiment: "pos", body: "Sourced from 3 Taiwan supply-chain partners." },
      { src: "TECH", head: "Reclaimed 50-DMA, relative strength vs SOX positive", meta: "Alpha Vantage · computed", sentiment: "pos", body: "Short interest down 3 consecutive weeks." },
    ],
    seed: 12, drift: 0.0018, vol: 0.027,
  },
  {
    tk: "META", name: "Meta Platforms, Inc.", signal: "BUY", conf: 64, px: 512.88, chgPct: +1.33,
    rr: 2.3, entry: 510, stop: 492, target: 558, mcap: "1.30T", vol: "18.4M", pe: 29.1, ts: "08:42:10",
    style: "position", win: 60, sources: ["EDGAR", "FINN"],
    headline: "Insider buy cluster meets ad-revenue acceleration.",
    narrative: "Three insiders filed Form 4 purchases totaling $2.8M — the first cluster buy since October 2023 — as scraped ad data shows revenue re-accelerating.",
    rationale: [
      { src: "EDGR", head: "Form 4: 3 insiders bought $2.8M on 4/17", meta: "EDGAR", sentiment: "pos", body: "First cluster buy since Oct 2023." },
      { src: "FINN", head: "Scraped ad-spend data inflecting higher", meta: "Finnhub · alt-data", sentiment: "pos", body: "Reseller channel checks point to a stronger quarter." },
    ],
    seed: 17, drift: 0.0013, vol: 0.018,
  },
  {
    tk: "PLTR", name: "Palantir Technologies", signal: "BUY", conf: 61, px: 23.88, chgPct: +2.66,
    rr: 2.6, entry: 23.8, stop: 21.4, target: 28.5, mcap: "51B", vol: "44.2M", pe: 214, ts: "07:58:19",
    style: "intraday", win: 66, sources: ["GNEW", "X"],
    headline: "New $480M DoD ceiling raise lifts the bid.",
    narrative: "SAM.gov shows a $480M contract-ceiling increase, and WSB mentions are up 34% week-over-week. A momentum-led entry with a tight stop.",
    rationale: [
      { src: "GNEW", head: "SAM.gov: $480M DoD contract ceiling raised", meta: "Google News · gov feed", sentiment: "pos", body: "Expands maximum order value on an existing vehicle." },
      { src: "X", head: "WSB mentions +34% WoW", meta: "Twitter/X", sentiment: "neu", body: "Retail attention building into the contract news." },
    ],
    seed: 21, drift: 0.0016, vol: 0.034,
  },
  {
    tk: "AAPL", name: "Apple Inc.", signal: "HOLD", conf: 54, px: 184.12, chgPct: +0.21,
    rr: 1.2, entry: null, stop: null, target: null, mcap: "2.82T", vol: "42.1M", pe: 28.4, ts: "09:02:55",
    style: "position", win: 58, sources: ["CAL", "TECH"],
    headline: "Earnings in 6 days — compressed range, neutral flow.",
    narrative: "A 14-day Bollinger squeeze at a 10-month low with earnings on 4/25. No directional edge until the catalyst clears — the engine stays flat.",
    rationale: [
      { src: "CAL", head: "Earnings 4/25 after close; iPhone mix in focus", meta: "Earnings Calendar", sentiment: "neu", body: "Consensus EPS $1.52 (+4.1% YoY); implied move ±4.8%." },
      { src: "TECH", head: "Bollinger Band squeeze — 14d width at 10-month low", meta: "Alpha Vantage · computed", sentiment: "neu", body: "Directional bias unclear until a catalyst resolves it." },
    ],
    seed: 15, drift: 0.0004, vol: 0.013,
  },
  {
    tk: "MSFT", name: "Microsoft Corporation", signal: "HOLD", conf: 48, px: 421.05, chgPct: +0.20,
    rr: 1.4, entry: null, stop: null, target: null, mcap: "3.13T", vol: "21.0M", pe: 37.6, ts: "08:12:03",
    style: "position", win: 64, sources: ["TECH", "CAL"],
    headline: "Azure growth intact; valuation stretched vs peers.",
    narrative: "The trend is healthy but the multiple is extended relative to mega-cap peers. The signal stays neutral pending a better entry.",
    rationale: [
      { src: "TECH", head: "Above all major MAs, but RSI elevated", meta: "Alpha Vantage · computed", sentiment: "neu", body: "Trend persistence positive; momentum cooling." },
      { src: "CAL", head: "No near-term catalyst on the calendar", meta: "Earnings Calendar", sentiment: "neu", body: "Next print outside the active window." },
    ],
    seed: 14, drift: 0.0009, vol: 0.014,
  },
];

const WATCHLIST = SIGNALS; // dashboard alias

const CHART_CACHE = {};
function chartFor(tk) {
  if (CHART_CACHE[tk]) return CHART_CACHE[tk];
  const w = SIGNALS.find((x) => x.tk === tk);
  const raw = genSeries(w.seed * 97 + 5, 90, 100, w.drift, w.vol);
  const k = w.px / raw[raw.length - 1];
  CHART_CACHE[tk] = raw.map((v) => v * k);
  return CHART_CACHE[tk];
}
function sparkFor(tk) { return chartFor(tk).slice(-30); }
function winSparkFor(tk) {
  const w = SIGNALS.find((x) => x.tk === tk);
  const rnd = mulberry32(w.seed * 31 + 7);
  const out = [];
  for (let i = 0; i < 12; i++) out.push(w.win + (rnd() - 0.5) * 14);
  out[11] = w.win;
  return out;
}

// ---- Real ticker tape (data.js) ----
const TICKER_TAPE = [
  { tk: "SPY", verb: "HOLD", px: "518.22", chg: "+0.84%" },
  { tk: "QQQ", verb: "BUY", px: "438.11", chg: "+1.22%" },
  { tk: "NVDA", verb: "BUY", px: "1,248.32", chg: "+2.84%" },
  { tk: "AAPL", verb: "HOLD", px: "184.12", chg: "+0.21%" },
  { tk: "TSLA", verb: "SELL", px: "164.82", chg: "-2.43%" },
  { tk: "MSFT", verb: "HOLD", px: "421.05", chg: "+0.20%" },
  { tk: "META", verb: "BUY", px: "512.88", chg: "+1.33%" },
  { tk: "AMD", verb: "BUY", px: "162.44", chg: "+2.02%" },
  { tk: "SMCI", verb: "SELL", px: "892.11", chg: "-3.08%" },
  { tk: "PLTR", verb: "BUY", px: "23.88", chg: "+2.66%" },
  { tk: "VIX", verb: "HOLD", px: "14.82", chg: "-3.95%" },
];

// ---- Telegram delivery feed (data.js WA_MESSAGES, re-skinned) ----
const TELEGRAM_FEED = [
  { dir: "out", time: "07:58", verb: "BUY", tk: "PLTR", px: "23.88", body: "Conf 61% · R:R 2.6\n• New $480M DoD ceiling (SAM.gov)\n• WSB sentiment +34% WoW\nEntry 23.80 / Stop 21.40 / TP 28.50" },
  { dir: "out", time: "08:31", verb: "SELL", tk: "SMCI", px: "892.11", body: "Conf 81% · R:R 2.9\n• Short thread +840k views\n• Margin concerns propagate\nEntry 890 / Stop 948 / TP 760" },
  { dir: "out", time: "08:42", verb: "BUY", tk: "META", px: "512.88", body: "Conf 64% · R:R 2.3\n• 3 insiders filed Form 4 ($2.8M)\n• Ad-rev acceleration in scraped data\nEntry 510 / Stop 492 / TP 558" },
  { dir: "in", time: "08:48", body: "nice one, taking META at open" },
  { dir: "out", time: "09:14", verb: "SELL", tk: "TSLA", px: "164.82", body: "Conf 72% · R:R 2.1\n• Q1 deliveries miss (−10.5% YoY)\n• SEC 8-K $412M warranty reserve\nEntry 164.50 / Stop 172 / TP 148" },
];

// ---- Backtest engine (parameter-driven, deterministic) ----
function runBacktest({ confMin, holdDays, stopPct, sources }) {
  const nSources = Object.values(sources).filter(Boolean).length || 1;
  const edge = 0.00042 * nSources * (confMin / 60) * Math.min(1.6, holdDays / 6 + 0.7);
  const vol = 0.0095 * (1.25 - confMin / 200) * (1 + (10 - stopPct) * 0.012);
  const seed = Math.round(confMin * 7 + holdDays * 131 + stopPct * 17 + nSources * 999);
  const rnd = mulberry32(seed);
  const n = 240;
  const curve = [100000];
  let peak = 100000, maxDD = 0, wins = 0, trades = 0, sumR = 0, sumR2 = 0;
  for (let i = 1; i < n; i++) {
    let r = edge + (rnd() - 0.5) * 2 * vol;
    if (r < -stopPct / 100) r = -stopPct / 100;
    const v = curve[i - 1] * (1 + r);
    curve.push(v);
    if (v > peak) peak = v;
    const dd = (peak - v) / peak;
    if (dd > maxDD) maxDD = dd;
    if (i % Math.max(1, Math.round(holdDays / 2)) === 0) { trades++; if (r > 0) wins++; }
    sumR += r; sumR2 += r * r;
  }
  const mean = sumR / (n - 1);
  const sd = Math.sqrt(Math.max(1e-9, sumR2 / (n - 1) - mean * mean));
  const sharpe = (mean / sd) * Math.sqrt(252);
  const total = curve[n - 1] / curve[0] - 1;
  const cagr = Math.pow(1 + total, 252 / n) - 1;
  let p2 = curve[0];
  const ddCurve = curve.map((v) => { if (v > p2) p2 = v; return (p2 - v) / p2; });
  return {
    curve, ddCurve,
    metrics: { cagr: cagr * 100, sharpe, winRate: trades ? (wins / trades) * 100 : 0, maxDD: maxDD * 100, trades: trades * 8, final: curve[n - 1] },
  };
}

const FEATURES = [
  { t: "Institutional flow, decoded", d: "SEC 13F filings and Form 4 insider buys — the engine fires the moment institutions add.", chart: "spark", seed: 41, color: "bull", stat: "EDGAR · polled 60s" },
  { t: "Options sweeps, caught live", d: "Volume above 5× open interest, OTM call/put spikes and IV term structure — flagged in seconds.", chart: "bars", seed: 42, color: "bull", stat: "2.3s avg latency" },
  { t: "Every signal, backtested", d: "Win rate, Sharpe and max drawdown by horizon for every pattern — audited on a public ledger.", chart: "equity", seed: 43, color: "bull", stat: "61.4% 7-day win rate" },
  { t: "Macro gates everything", d: "VIX regime, yield curve, breadth and the calendar gate every signal — no longs into a breaking tape.", chart: "regime", seed: 44, color: "neutral", stat: "4 regime states" },
];

const HOME_STATS = [
  { n: 61.4, dp: 1, suffix: "%", l: "7-day win rate", s: "Across 2,194 closed signals" },
  { n: 1.84, dp: 2, suffix: "", l: "Sharpe ratio", s: "Annualized, last 90 days" },
  { n: 18.2, dp: 1, suffix: "%", prefix: "+", l: "YTD return", s: "Paper-traded, equal-weight" },
  { n: 2.3, dp: 1, suffix: "s", l: "Median latency", s: "Source → Telegram delivery" },
];

Object.assign(window, {
  mulberry32, genSeries, SIGNALS, WATCHLIST, chartFor, sparkFor, winSparkFor,
  TICKER_TAPE, TELEGRAM_FEED, runBacktest, FEATURES, HOME_STATS,
});
