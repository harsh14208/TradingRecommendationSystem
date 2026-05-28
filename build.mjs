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
 * Output: dist/app-bundle.js (~same size as all JSX files combined, minified)
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

import { readFileSync, writeFileSync, mkdirSync, statSync, watch } from 'fs';
import { transformSync } from 'esbuild';

// Load order must match <script type="text/babel"> order in the HTML.
// Earlier files define globals consumed by later files.
const JSX_FILES = [
  'app.auth.jsx',       // defines React hook globals (useState, useEffect, …)
  'app.constants.jsx',  // TIERS, COLORS, API helpers
  'app.ui.jsx',         // shared UI components
  'app.signal.jsx',     // SignalCard, SignalDetail
  'app.views.jsx',      // tab views (Dashboard, Backtest, …)
  'app.modals.jsx',     // modal components
  'app.analysis.jsx',   // AnalysisView (optional heavy tab)
  'app.jsx',            // root <App/> + ReactDOM.createRoot render
];

const OUT_DIR = 'dist';
const OUT_FILE = `${OUT_DIR}/app-bundle.js`;

function build() {
  const start = Date.now();
  mkdirSync(OUT_DIR, { recursive: true });

  const parts = JSX_FILES.map((file) => {
    const source = readFileSync(file, 'utf8');
    const result = transformSync(source, {
      loader: 'jsx',
      // Classic transform: JSX → React.createElement() calls.
      // React is a global UMD (loaded via CDN script tag), so jsxImportSource
      // (automatic runtime) is not available here.
      jsx: 'transform',
      jsxFactory: 'React.createElement',
      jsxFragment: 'React.Fragment',
      target: 'es2019',       // Safari 12 / Chrome 73 — no format wrapping
      minify: true,
      sourcemap: 'inline',    // browser devtools show original JSX source
      sourcefile: file,
    });
    return result.code;
  });

  const bundle = parts.join('\n');
  writeFileSync(OUT_FILE, bundle);

  const kb = Math.round(bundle.length / 1024);
  console.log(`[build] ${OUT_FILE} — ${kb} KB (${Date.now() - start}ms)`);
}

// ── Entry point ────────────────────────────────────────────────────────────────

const isWatch = process.argv.includes('--watch');

build();

if (isWatch) {
  console.log('[build] Watching for changes…');
  const watched = new Set(JSX_FILES);
  for (const file of watched) {
    watch(file, () => {
      console.log(`[build] ${file} changed — rebuilding`);
      try { build(); } catch (e) { console.error('[build] Error:', e.message); }
    });
  }
}
