// App loader — loads esbuild-compiled bundle. Babel fallback is localhost-only.
// CSP: script-src 'self' (no 'unsafe-eval' required — bundle uses no eval).
//
// Path A (production): /dist/app-bundle.js — esbuild-compiled, no eval needed.
// Path B (dev): Babel CDN — ONLY on localhost. Never loads in production.
//
// To rebuild bundle after JSX changes:
//   node build.mjs   (requires esbuild binary — see build.mjs for setup)

(function selectAppPath() {
  var bundle = document.createElement('script');
  bundle.src = '/dist/app-bundle.js';
  bundle.onerror = function onBundleMissing() {
    var isLocal = location.hostname === 'localhost' || location.hostname === '127.0.0.1';
    if (!isLocal) {
      // Production: bundle is required. Show error — never fall back to Babel.
      console.error(
        '[Signal.Trade] FATAL: dist/app-bundle.js not found. ' +
        'Run `node build.mjs` to build the production bundle. ' +
        'Babel CDN fallback is disabled in production for security (CSP).'
      );
      document.body.innerHTML =
        '<div style="font-family:monospace;padding:2rem;color:var(--down)">' +
        '<b>App bundle missing.</b> Run <code>node build.mjs</code> and redeploy.' +
        '</div>';
      return;
    }
    // Localhost dev only: fall back to Babel CDN.
    console.warn('[Signal.Trade] Dev mode: Babel CDN fallback (localhost only).');
    var babel = document.createElement('script');
    babel.src = 'https://unpkg.com/@babel/standalone@7.29.0/babel.min.js';
    babel.integrity = 'sha384-m08KidiNqLdpJqLq95G/LEi8Qvjl/xUYll3QILypMoQ65QorJ9Lvtp2RXYGBFj1y';
    babel.crossOrigin = 'anonymous';
    babel.onload = function () { Babel.transformScriptTags(); };
    document.body.appendChild(babel);
  };
  document.body.appendChild(bundle);
})();
