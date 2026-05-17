/* ─── Tier constants ────────────────────────────────────────────────────────── */
const TIER_ORDER  = ["free","basic","pro"];
const TIER_COLORS = { free:"var(--text-faint)", basic:"var(--accent)", pro:"#7c3aed" };

/* ── ET timezone helpers (module-scope so all components can use them) ──────── */
const _etFmt = (date, opts) => {
  try {
    if (!date || isNaN(date.getTime())) return "—";
    return new Intl.DateTimeFormat("en-US", { timeZone: "America/New_York", ...opts }).format(date);
  } catch { return "—"; }
};

/** Parse an ISO string or "HH:MM" string safely into a Date. Returns null if invalid. */
const _parseTS = (iso) => {
  if (!iso || iso === "—") return null;
  // Reject bare time strings like "14:30" that aren't valid ISO dates
  if (/^\d{1,2}:\d{2}(:\d{2})?$/.test(iso)) return null;
  const d = new Date(iso);
  return isNaN(d.getTime()) ? null : d;
};

/** Format a UTC ISO string as "HH:MM ET", e.g. "14:32 ET" */
const fmtETTime = (iso) => {
  const d = _parseTS(iso);
  if (!d) return "—";
  return _etFmt(d, { hour: "2-digit", minute: "2-digit", hour12: false }) + " ET";
};

/** Format a UTC ISO string as "Apr 27, 14:32 EDT" */
const fmtETFull = (iso, abbr = "ET") => {
  const d = _parseTS(iso);
  if (!d) return "—";
  return _etFmt(d, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit", hour12: false }) + " " + abbr;
};

function hasTierAccess(tier, min, isOwner) {
  if (isOwner) return true;
  return TIER_ORDER.indexOf(tier || "free") >= TIER_ORDER.indexOf(min);
}

/* ─── Source abbreviation map (backend sends full names; badge is 22×22px) ─── */
const SRC_ABBR = {
  "Technical": "TA", "Options": "OPT", "Market Sentiment": "MS",
  "Market Breadth": "MB", "Fundamentals": "FND", "Insider": "IN",
  "Analyst": "AN", "Macro": "MC", "Social": "SOC", "SEC EDGAR": "SEC",
  "Fear & Greed": "F&G", "Earnings": "ERN", "FRED": "FED",
  "Finnhub": "FH", "Backtest": "BT", "Relative Strength": "RS",
  "Sector RS": "SRS", "Short Interest": "SI", "Signal Cluster": "SC",
  "Stat Arb": "SA", "Orthogonalization": "OG", "13F": "13F", "Dark Pool": "DP",
};
const srcAbbr = s => SRC_ABBR[s] || (s || "?").slice(0, 4).toUpperCase();

/* ─── Glossary ─────────────────────────────────────────────────────────────── */
const GLOSSARY = {
  BUY:       "The system thinks the price is likely to go UP.",
  SELL:      "The system thinks the price is likely to go DOWN.",
  HOLD:        "No clear edge — wait for a better setup.",
  CONFIDENCE:  "How strong the evidence is (0–100%). Computed from 65+ independent signal blocks across 11 scoring families using a sigmoid formula capped at 84%. The 84% ceiling reflects empirical calibration — signals above 80% raw confidence historically have only 50–67% actual win rates. Higher = more data sources agree. Not a guarantee of profit.",
  "R:R":       "Risk-to-Reward ratio. e.g. 1.5 means you risk $1 to potentially make $1.50. Aim for ≥1.5 on swing trades.",
  RR:          "Risk-to-Reward ratio. e.g. 1.5 means you risk $1 to potentially make $1.50.",
  ENTRY:       "The suggested price at which to open the trade — typically near the current market price.",
  STOP:        "Stop-Loss: the price at which to exit immediately if wrong. This caps your maximum loss on the trade.",
  TARGET:      "Take-Profit: the price to exit when the trade is working. Based on 3× the risk amount.",
  SENTIMENT:   "Aggregated news & social sentiment from −1 (very bearish) to +1 (very bullish). Includes Finnhub news and StockTwits.",
  VIX:         "CBOE Volatility Index — the market's 'fear gauge'. Below 15 = calm markets (bullish for stocks). Above 25 = elevated fear. Above 30 = panic (often a contrarian buy signal).",
  VIX3M:       "3-month forward VIX. When spot VIX > VIX3M (backwardation), it signals acute fear — historically a contrarian buy signal.",
  "YIELD CURVE":"The spread between 10-year and 2-year US Treasury yields. Positive = healthy economy (10Y > 2Y). Negative (inverted) = recession warning — has preceded every US recession since 1955.",
  "MARKET BREADTH":"Percentage of S&P 500 stocks trading above their 200-day moving average. Above 70% = broad market participation (bullish). Below 30% = most stocks in downtrend (bearish).",
  "CBOE P/C":  "CBOE Put/Call ratio. High (>1.15) = excessive fear/put buying → contrarian bullish. Low (<0.65) = excessive call buying/complacency → contrarian bearish.",
  NAAIM:       "National Association of Active Investment Managers exposure index. How much of client assets active managers have in equities. Near 100% = fully invested (limited upside fuel). Near 0% = maximum defensive (contrarian bullish).",
  COT:         "CFTC Commitment of Traders — leveraged fund net positioning in S&P 500 futures. When hedge funds are extremely net short, a short squeeze is likely (contrarian bullish). When extremely net long, the trade is crowded.",
  DXY:         "US Dollar Index — measures the dollar vs a basket of 6 major currencies. Rising dollar hurts US multinationals' overseas earnings. Falling dollar boosts export revenues.",
  "CU/GOLD":   "Copper/Gold ratio. Copper = industrial demand, Gold = safe-haven. Rising ratio → economic growth expanding (risk-on). Falling ratio → growth concerns, flight to safety.",
  "CYCLE STAGE":"Economic cycle stage based on yield curve, VIX, credit spreads and SPX trend. Early cycle favours cyclicals (XLY, XLF). Mid cycle favours tech (XLK). Late cycle favours defensives (XLV, XLP). Recession favours gold and utilities.",
  "P(SUCCESS)": "Bayesian probability of this signal being profitable, estimated from the outcomes of similar historical signals. Uses Laplace smoothing to avoid overconfidence on small samples. Not a guarantee — market conditions change.",
  "1D":        "1-day hold: close the trade at end of next trading day. Shortest horizon — highest noise, best for momentum.",
  "3D":        "3-day hold: close after 3 trading sessions. Balances signal clarity with holding risk.",
  "7D":        "7-day (one week) hold: primary horizon used for win-rate tracking.",
  "14D":       "14-day (two week) hold: position-style trades with wider stops.",
  P10:         "10th percentile outcome — worst-case realistic result (90% of similar signals did better than this).",
  P90:         "90th percentile outcome — best-case realistic result (only 10% of similar signals did better than this).",
  SHARPE:      "Sharpe ratio: return per unit of risk. Above 1.0 is good. Above 2.0 is excellent. Negative = returns don't compensate for risk.",
  "MAX DD":    "Maximum Drawdown: the largest peak-to-trough loss during the period. Tells you the worst sustained loss you'd have experienced.",
  CALMAR:      "Calmar ratio: annualised return divided by maximum drawdown. Above 1.0 means returns justify the drawdown risk.",

  /* ── Technical indicators ── */
  MACD:        "Moving Average Convergence/Divergence. Measures momentum by comparing two EMAs (12-day vs 26-day). A bullish crossover (histogram flips positive) signals trend strength building. A bearish crossover signals weakening.",
  RSI:         "Relative Strength Index (14-day). Momentum oscillator 0–100. Below 30 = oversold / likely bounce. Above 70 = overbought / pullback risk. Divergence from price is a powerful reversal signal.",
  "RSI DIVERGENCE": "When price makes a new high/low but RSI does NOT confirm it. Bearish divergence: price up, RSI down = momentum fading. Bullish divergence: price down, RSI up = selling pressure exhausting. One of the most reliable reversal signals.",
  OBV:         "On-Balance Volume. Running total of volume that adds on up-days and subtracts on down-days. Rising OBV = smart money accumulating even if price is flat. Falling OBV = distribution under the surface.",
  CMF:         "Chaikin Money Flow. Measures buying vs selling pressure using both price position and volume over 20 days. Above +0.15 = sustained institutional accumulation. Below −0.15 = sustained distribution. Flat CMF on rising price = weak hands buying.",
  ADX:         "Average Directional Index. Measures TREND STRENGTH, not direction. Above 25 = a real trend exists (follow it). Below 20 = choppy/ranging market (oscillator signals more reliable). Use +DI vs −DI to determine direction.",
  FDI:         "Fractal Dimension Index. Measures how 'linear' price movement is. Below 1.25 = near-linear trending move — breakout signals are reliable. Above 1.45 = fractal/chaotic price action — breakouts are traps, mean-reversion signals work better.",
  HURST:       "Hurst Exponent. Classifies price regime. Above 0.60 = persistent trending (momentum works). Near 0.50 = random walk. Below 0.40 = anti-persistent mean-reverting (buy oversold, sell overbought). Changes the type of signal to trust.",
  VWAP:        "Volume-Weighted Average Price (20-day rolling). The average cost basis of all participants over 20 days. Price above VWAP = buyers in profit, less overhead supply. Price below VWAP = average participant underwater, creates overhead selling pressure at break-even.",
  SUPERTREND:  "ATR-based trailing stop indicator. In bullish mode = dynamic rising support floor. In bearish mode = descending resistance ceiling. A flip from bearish to bullish is one of the cleanest momentum reversal signals — ATR filters out noise.",
  STOCHASTIC:  "Stochastic Oscillator %K/%D. Compares closing price to the high-low range over 14 days. Below 20 = near recent lows (oversold). Above 80 = near recent highs (overbought). A bullish cross in the oversold zone is a high-probability setup.",
  "WILLIAMS %R": "Momentum oscillator measuring where price sits within its 14-day range. Below −80 = near bottom of range (bounce potential). Above −20 = near top of range (distribution risk). Fast-moving — fires earlier than RSI but noisier.",
  CCI:         "Commodity Channel Index. Measures price deviation from its statistical average. Beyond ±150 = statistically extreme (2+ standard deviations). Extreme oversold (< −150) often precedes sharp reversals. Used to detect trend exhaustion.",
  MFI:         "Money Flow Index. Volume-weighted RSI. Below 20 = heavy money outflow (volume-confirmed oversold). Above 80 = heavy money inflow (volume-confirmed overbought). More reliable than RSI alone because it incorporates actual buying/selling volume.",
  KELTNER:     "Keltner Channel (20-period, 2×ATR). ATR-based channel that filters out volatility noise better than Bollinger Bands. A breakout above the upper channel = genuine momentum, not just volatility expansion. Inside the channel = range-bound.",
  DONCHIAN:    "Donchian Channel breakout (20-day high/low). The original Turtle Trading signal. Breaking the 20-day high = new momentum establishing. Breaking the 20-day low = new downtrend beginning. Simple but very reliable for trend-following.",
  ICHIMOKU:    "Ichimoku Cloud system. TK Cross (Tenkan/Kijun) = momentum signal. Cloud = trend filter and support/resistance zone. Price above a bullish (green) cloud = confirmed uptrend. Chikou span = lagging confirmation line. Requires all components to align for highest conviction.",
  ZSCORE:      "Z-score = how many standard deviations price is from its 20-day mean. Beyond ±2.0 = statistically stretched (extreme 5% territory). Beyond ±2.5 = extreme 1% territory — high-probability mean reversion setup. Does NOT predict timing, only statistical extremes.",
  PIVOTS:      "Classic pivot points calculated from yesterday's High, Low, and Close. S1 = first support below. R1 = first resistance above. These levels act as intraday magnets — price often stalls or reverses at these zones.",
  "PRICE STRUCTURE": "Swing structure analysis. Higher Highs + Higher Lows (HH/HL) = healthy uptrend — bias long. Lower Highs + Lower Lows (LH/LL) = confirmed downtrend — bias short. Structure breaks are early warning signals for trend changes.",

  /* ── Cross-signal and meta ── */
  "ORTHOGONAL ALPHA": "Signals from genuinely independent data pipelines (filings, fundamentals, positioning, macro) that all agree with the same directional thesis. Unlike a 5th technical indicator, each orthogonal source adds truly new information — convergence across uncorrelated sources raises statistical confidence that this isn't a coincidence.",
  "SIGNAL CLUSTER":   "6+ independent signal CATEGORIES (Technical, Options, Institutional, Analyst, Macro, Fundamentals, Sentiment, Earnings, Social) all pointing the same direction simultaneously. Historical studies show that multi-category agreement produces meaningfully higher win rates than any single category alone.",
  "PLATT CALIBRATION":"Empirical confidence correction. The model's raw score is blended toward the actual historical win rate observed in thousands of resolved signals in the same confidence band. If signals at 72% raw confidence have historically won only 47% of the time, the calibrated output reflects that reality.",
  "FACTOR MINING":    "Weekly automated backtest that ranks all source combinations (e.g. 'Technical+Analyst', 'Options+Macro') by out-of-sample Sharpe ratio. Combinations with historically proven edges get small boosts; combinations with poor track records get small penalties. Refit every Sunday.",
  "SECTOR RS":        "Relative Strength vs sector ETF (1-month return). Stock leading its sector by >8% signals stock-specific institutional demand. 'Sector Trap': leading a sector that itself lags SPY often means the entire sector is being sold — the leader follows eventually.",
  "13F":              "Quarterly 13F institutional filings from major funds. Shows whether institutions are increasing or decreasing their stake. Consecutive quarterly buying (QoQ Rising) = growing conviction. Consecutive selling (QoQ Falling) = early exit signal from smart money.",
  "STAT ARB":         "Statistical Arbitrage via cointegration. Two stocks that historically move together (≥70% correlation) have diverged beyond 2 standard deviations. Mean-reversion trade — the spread has historically closed within 5–15 trading days. Pure relative-value signal, market-direction neutral.",
  "ELLIOTT WAVE":     "Elliott Wave Theory analyzes market cycles. Wave 3 is the strongest impulse wave (highly bullish/bearish). Wave 5 indicates trend exhaustion. Wave C marks the end of a correction, signaling a high-probability reversal.",
  "GANN ANALYSIS":    "W.D. Gann's theory uses geometric angles to track price/time balance. A 1x1 angle represents a perfectly balanced 45-degree trend. Respecting the 1x1 angle confirms strong, sustainable momentum.",
  "DARK POOL":        "Off-exchange block trades used by institutional 'whales' to hide large orders. Heavy net positive flow signals stealth accumulation. Heavy net negative flow signals stealth distribution. Highly predictive since it tracks actual smart-money execution.",
  "FTD":              "Fails-to-Deliver. When short sellers fail to deliver borrowed shares. High FTDs and Reg SHO Threshold list inclusion strongly signal forced mechanical buying/short squeezes.",
  "GEX":              "Gamma Exposure. Measures market maker options positioning. Positive GEX means dealers trade against the trend (dampening volatility). Negative GEX means dealers trade with the trend (amplifying volatility and breakouts).",
  "LEVEL 2":          "Level 2 Order Book. Shows the real-time depth of resting bid (buy) and ask (sell) limit orders. A heavy imbalance (e.g., 4x more bids) creates a structural support floor.",
  "CORP ACTIONS":     "Corporate Actions like Accelerated Share Repurchases (ASR). When a company actively buys its own stock on the open market, it provides a persistent, mechanical bid that overrides technical weakness.",
};
