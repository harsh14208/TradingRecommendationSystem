/**
 * Signal.Trade frontend build — esbuild JSX transform + concatenate.
 *
 * Why not Vite bundling / ES modules?
 *   The JSX files share variables through global scope (each file exposes
 *   constants and components as top-level lets/consts that later files consume).
 *   Converting to ES module imports/exports would require touching every file.
 *   Instead: transform JSX → JS with esbuild, concatenate in the same order
 *   as the existing <script type="text/babel"> tags, emit one <script src>.
 *   Zero changes to any JSX file required.
 *
 * Outputs:
 *   dist/app-bundle.js    — main app (Trading Recommendation System.html)
 *   dist/site-bundle.js   — landing page (landing.html)
 *
 * Usage:
 *   npm install
 *   npm run build          # one-shot
 *   npm run build:watch    # rebuild on file change (dev server mode)
 *
 * After running: update Trading Recommendation System.html to load
 *   /dist/app-bundle.js instead of Babel CDN + individual JSX files,
 *   and remove 'unsafe-eval' from CSP in backend/main.py.
 */

import { readFileSync, writeFileSync, mkdirSync, watch } from 'fs';
import { transformSync } from 'esbuild';

const ESBUILD_OPTS = {
  loader: 'jsx',
  jsx: 'transform',
  jsxFactory: 'React.createElement',
  jsxFragment: 'React.Fragment',
  target: 'es2019',
  minify: true,
  sourcemap: 'inline',
};

// Load order must match <script type="text/babel"> order in the HTML.
// Earlier files define globals consumed by later files.
const APP_FILES = [
  'app.auth.jsx',       // defines React hook globals (useState, useEffect, …)
  'app.constants.jsx',  // TIERS, COLORS, API helpers
  'app.ui.jsx',         // shared UI components
  'app.signal.jsx',     // SignalCard, SignalDetail
  'app.views.jsx',      // tab views (Dashboard, Backtest, …)
  'app.modals.jsx',     // modal components
  'app.analysis.jsx',   // AnalysisView (optional heavy tab)
  'app.jsx',            // root <App/> + ReactDOM.createRoot render
];

// Landing page — standalone single-file build.
const LANDING_FILES = ['site.jsx'];

// Mobile PWA — standalone single-file build.
const MOBILE_FILES = ['mobile.jsx'];

const TARGETS = [
  { files: APP_FILES,     out: 'dist/app-bundle.js' },
  { files: LANDING_FILES, out: 'dist/site-bundle.js' },
  { files: MOBILE_FILES,  out: 'dist/mobile-bundle.js' },
];

const OUT_DIR = 'dist';

function buildTarget({ files, out }) {
  const start = Date.now();
  mkdirSync(OUT_DIR, { recursive: true });

  const parts = files.map((file) => {
    const source = readFileSync(file, 'utf8');
    const result = transformSync(source, { ...ESBUILD_OPTS, sourcefile: file });
    return result.code;
  });

  const bundle = parts.join('\n');
  writeFileSync(out, bundle);

  const kb = Math.round(bundle.length / 1024);
  console.log(`[build] ${out} — ${kb} KB (${Date.now() - start}ms)`);
}

function buildAll() {
  for (const target of TARGETS) {
    try {
      buildTarget(target);
    } catch (e) {
      console.error(`[build] ${target.out} failed:`, e.message);
    }
  }
}

// ── Entry point ────────────────────────────────────────────────────────────────

const isWatch = process.argv.includes('--watch');

buildAll();

if (isWatch) {
  console.log('[build] Watching for changes…');
  const allFiles = new Set(TARGETS.flatMap((t) => t.files));
  for (const file of allFiles) {
    watch(file, () => {
      console.log(`[build] ${file} changed — rebuilding`);
      // Rebuild only the target(s) that include this file.
      for (const target of TARGETS) {
        if (target.files.includes(file)) {
          try { buildTarget(target); } catch (e) { console.error('[build] Error:', e.message); }
        }
      }
    });
  }
}
