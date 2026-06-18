/* global React */
// SIGNAL.TRADE cinematic — shared UI primitives.
// Animated count-up that re-runs whenever `value` changes.
function useCountUp(value, dur = 900) {
  const [disp, setDisp] = useState(value);
  const fromRef = useRef(value);
  useEffect(() => {
    const from = fromRef.current;
    if (from === value) return;
    let raf, t0;
    const step = (t) => {
      if (!t0) t0 = t;
      const p = Math.min(1, (t - t0) / dur);
      const e = 1 - Math.pow(1 - p, 3);
      setDisp(from + (value - from) * e);
      if (p < 1) raf = requestAnimationFrame(step);
      else fromRef.current = value;
    };
    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [value, dur]);
  return disp;
}

function Num({ value, dp = 1, prefix = "", suffix = "", dur = 900 }) {
  const v = useCountUp(value, dur);
  return <span className="mono">{prefix}{v.toLocaleString("en-US", { minimumFractionDigits: dp, maximumFractionDigits: dp })}{suffix}</span>;
}

function colorVar(c) {
  return c === "bear" ? "var(--bear)" : c === "neutral" || c === "neut" ? "var(--neutral)" : "var(--bull)";
}

// SVG sparkline with optional area fill.
function Spark({ data, w = 120, h = 36, color = "bull", fill = true, sw = 1.5 }) {
  const min = Math.min(...data), max = Math.max(...data);
  const rng = max - min || 1;
  const pts = data.map((v, i) => [
    (i / (data.length - 1)) * w,
    h - 3 - ((v - min) / rng) * (h - 6),
  ]);
  const d = pts.map((p, i) => `${i ? "L" : "M"}${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(" ");
  const col = colorVar(color);
  const gid = useRef("g" + Math.random().toString(36).slice(2, 8)).current;
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} style={{ display: "block", overflow: "visible" }}>
      {fill && (
        <defs>
          <linearGradient id={gid} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={col} stopOpacity="0.22"></stop>
            <stop offset="100%" stopColor={col} stopOpacity="0"></stop>
          </linearGradient>
        </defs>
      )}
      {fill && <path d={`${d} L${w},${h} L0,${h} Z`} fill={`url(#${gid})`}></path>}
      <path d={d} fill="none" stroke={col} strokeWidth={sw} strokeLinejoin="round" strokeLinecap="round"></path>
      <circle cx={pts[pts.length - 1][0]} cy={pts[pts.length - 1][1]} r="2.2" fill={col}></circle>
    </svg>
  );
}

// Mini bar chart (e.g. options volume).
function MiniBars({ seed = 1, n = 18, w = 120, h = 36, color = "bull" }) {
  const rnd = mulberry32(seed);
  const bars = Array.from({ length: n }, () => 0.18 + rnd() * 0.82);
  const bw = w / n;
  const col = colorVar(color);
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} style={{ display: "block" }}>
      {bars.map((v, i) => (
        <rect key={i} x={i * bw + 1} y={h - v * h} width={Math.max(1, bw - 2)} height={v * h} rx="1"
          fill={col} opacity={i === n - 3 ? 1 : 0.22 + v * 0.3}></rect>
      ))}
    </svg>
  );
}

function SignalBadge({ signal, size = "md" }) {
  const cls = signal === "BUY" ? "buy" : signal === "SELL" ? "sell" : "hold";
  const col = signal === "BUY" ? "var(--bull)" : signal === "SELL" ? "var(--bear)" : "var(--neutral)";
  const bg = signal === "BUY" ? "var(--bull-soft)" : signal === "SELL" ? "var(--bear-soft)" : "var(--neutral-soft)";
  const pad = size === "lg" ? "4px 12px" : "2px 8px";
  const fs = size === "lg" ? 12 : 10;
  return (
    <span className={`mono ${cls}`} style={{
      color: col, background: bg, padding: pad, borderRadius: 5,
      fontSize: fs, fontWeight: 700, letterSpacing: "0.08em",
      boxShadow: `inset 0 0 0 1px ${signal === "BUY" ? "rgba(34,211,238,0.25)" : signal === "SELL" ? "rgba(251,77,109,0.25)" : "rgba(251,191,36,0.25)"}`,
    }}>{signal}</span>
  );
}

// Confidence meter — thin segmented bar.
function ConfMeter({ conf, color }) {
  const col = color || (conf >= 70 ? "var(--bull)" : conf >= 55 ? "var(--neutral)" : "var(--text-faint)");
  return (
    <div style={{ display: "flex", gap: 2, alignItems: "center" }}>
      {Array.from({ length: 10 }, (_, i) => (
        <div key={i} style={{
          width: 5, height: 10, borderRadius: 1.5,
          background: i < Math.round(conf / 10) ? col : "rgba(255,255,255,0.08)",
        }}></div>
      ))}
    </div>
  );
}

function LiveDot({ color = "" }) { return <span className={`live-dot ${color}`}></span>; }

// ── Canonical brand mark — SINGLE SOURCE OF TRUTH ──────────────────────────
// Stylized "S" with an up-right trend arrow, drawn in the live theme accent
// (--bull). The static brand assets (favicon.svg, logo-full.svg, favicon.png,
// logo-icon*.png, apple-touch-icon.png) are GENERATED from these exact paths
// by `python frontend/scripts/generate_brand_assets.py`. Edit the paths here,
// then re-run that script so the files can never drift from the in-app mark.
const BRAND_MARK_STROKE = 3.6;
const BRAND_MARK_PATHS = [
  "M21.4 11.2c0-3.4-4.1-4.8-7.7-3.5-3.3 1.2-3.5 5-.2 6.4l3.6 1.5c3.3 1.4 3.1 5.2-.2 6.5-3.6 1.3-7.7-.1-7.7-3.6", // S curve
  "M18.6 13.4 25.3 6.7",          // arrow shaft
  "M20.4 6.4 25.6 6.4 25.6 11.6", // arrow head
];
function BrandMark({ size = 22 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" fill="none" aria-hidden="true"
      stroke="var(--bull)" strokeWidth={BRAND_MARK_STROKE} strokeLinecap="round" strokeLinejoin="round"
      style={{ display: "block", flex: "none" }}>
      {BRAND_MARK_PATHS.map((d, i) => <path key={i} d={d}></path>)}
    </svg>
  );
}

function Logo({ go, 'aria-label': ariaLabel = "SIGNAL.TRADE dashboard" }) {
  return (
    <button onClick={() => go && go("dashboard")} aria-label={ariaLabel} style={{ background: "none", border: "none", padding: 0, display: "flex", alignItems: "center", gap: 9, cursor: "pointer" }}>
      <BrandMark size={22}></BrandMark>
      <span className="mono" style={{ fontSize: 13, fontWeight: 700, letterSpacing: "0.08em", color: "var(--text)" }}>
        SIGNAL<span style={{ color: "var(--bull)" }}>.</span>TRADE
      </span>
    </button>
  );
}

// Shared viewport hook — true below `bp`px. Used for mobile-only behaviours.
function useIsMobile(bp = 860) {
  const [m, setM] = useState(() => typeof window !== "undefined" && window.matchMedia(`(max-width:${bp}px)`).matches);
  useEffect(() => {
    const mq = window.matchMedia(`(max-width:${bp}px)`);
    const fn = (e) => setM(e.matches);
    mq.addEventListener("change", fn);
    setM(mq.matches);
    return () => mq.removeEventListener("change", fn);
  }, [bp]);
  return m;
}

// Shared back affordance for legacy full-page views / drawers (replaces the
// old "× Close" buttons so every page dismisses with a consistent Back).
function BackButton({ onClick, style }) {
  return (
    <button className="btn ghost" onClick={onClick} aria-label="Back"
      style={{ display: "inline-flex", alignItems: "center", gap: 6, ...style }}>
      <Icon name="arrow-left" size={14}></Icon>
      <span style={{ fontSize: 12 }}>Back</span>
    </button>
  );
}

// Skeleton-wrapped loader: shows skeleton for `ms` then children (simulated async).
function Defer({ ms = 600, skeleton, children }) {
  const [ready, setReady] = useState(false);
  useEffect(() => { const t = setTimeout(() => setReady(true), ms); return () => clearTimeout(t); }, [ms]);
  return ready ? children : skeleton;
}

function SkelBlock({ h = 80, style }) { return <div className="skel" style={{ height: h, ...style }}></div>; }

Object.assign(window, { useCountUp, Num, Spark, MiniBars, SignalBadge, ConfMeter, LiveDot, Logo, BrandMark, BackButton, useIsMobile, Defer, SkelBlock, colorVar });
