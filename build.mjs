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
  'app.auth.jsx',          // auth/session helpers (getToken, apiFetch, …)
  'app.constants.jsx',     // TIERS, helpers, glossary
  'cin.ui.jsx',            // cinematic shared primitives
  'cin.data.jsx',          // mock signal + market data (overridden by API later)
  'cin.market-data.jsx',   // mock market context
  'cin.home.jsx',          // Home page
  'cin.dashboard.jsx',     // Signal Dashboard
  'cin.market.jsx',        // Market Context
  'cin.backtest.jsx',      // Backtest Lab
  'cin.track.jsx',         // Track Record
  'cin.settings.jsx',      // Settings
  'cin.app.jsx',           // root shell + routing
];

// Landing page — standalone single-file build.
const LANDING_FILES = ['site.jsx'];

// Mobile PWA — standalone single-file build.
const MOBILE_FILES = ['mobile.jsx'];

// Reorganized 2026-06-13: JSX sources live in frontend/src, bundles emit to
// frontend/dist (served at /dist). Paths are relative to the repo root, where
// `node build.mjs` runs (CI + local).
const SRC_DIR = 'frontend/src';
const OUT_DIR = 'frontend/dist';

const TARGETS = [
  { files: APP_FILES,     out: 'app-bundle.js' },
  { files: LANDING_FILES, out: 'site-bundle.js' },
  { files: MOBILE_FILES,  out: 'mobile-bundle.js' },
];

function buildTarget({ files, out }) {
  const start = Date.now();
  mkdirSync(OUT_DIR, { recursive: true });

  const parts = files.map((file) => {
    const source = readFileSync(`${SRC_DIR}/${file}`, 'utf8');
    const result = transformSync(source, { ...ESBUILD_OPTS, sourcefile: file });
    return result.code;
  });

  const bundle = parts.join('\n');
  const outPath = `${OUT_DIR}/${out}`;
  writeFileSync(outPath, bundle);

  const kb = Math.round(bundle.length / 1024);
  console.log(`[build] ${outPath} — ${kb} KB (${Date.now() - start}ms)`);
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
    watch(`${SRC_DIR}/${file}`, () => {
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
