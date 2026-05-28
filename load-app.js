// App loader — selects between pre-compiled bundle (production) and
// Babel CDN + JSX files (dev fallback). Kept external to satisfy CSP
// (script-src 'self' without 'unsafe-inline').
//
// Path A (production): /dist/app-bundle.js — esbuild-compiled, no eval needed.
// Path B (dev): Babel CDN + type="text/babel" scripts — requires 'unsafe-eval' in CSP.
//
// To switch to production permanently:
//   1. npm install && npm run build   (generates dist/app-bundle.js)
//   2. Remove 'unsafe-eval' from backend/main.py SecurityHeadersMiddleware._SCRIPT_SRC

(function selectAppPath() {
  var bundle = document.createElement('script');
  bundle.src = '/dist/app-bundle.js';
  bundle.onerror = function loadBabelPath() {
    var babel = document.createElement('script');
    babel.src = 'https://unpkg.com/@babel/standalone@7.29.0/babel.min.js';
    babel.integrity = 'sha384-m08KidiNqLdpJqLq95G/LEi8Qvjl/xUYll3QILypMoQ65QorJ9Lvtp2RXYGBFj1y';
    babel.crossOrigin = 'anonymous';
    babel.onload = function() {
      // Babel processes <script type="text/babel"> tags already in the DOM.
      // These are ignored by the browser until Babel is present.
      Babel.transformScriptTags();
    };
    document.body.appendChild(babel);
  };
  document.body.appendChild(bundle);
})();
