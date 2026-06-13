(function () {
  var bundle = document.getElementById('site-bundle');
  if (!bundle || !window.React) {
    // Bundle absent (not yet built) — fall back to Babel for local dev only.
    if (location.hostname !== 'localhost' && location.hostname !== '127.0.0.1') {
      console.error('[Signal.Trade] dist/site-bundle.js missing. Run: npm install && npm run build');
      return;
    }
    var babelScript = document.createElement('script');
    babelScript.src = 'https://unpkg.com/@babel/standalone@7.29.0/babel.min.js';
    babelScript.onload = function () {
      console.warn('[Signal.Trade] Babel fallback active — run npm run build for production.');
      var s = document.createElement('script');
      s.type = 'text/babel';
      s.src = '/site.jsx';
      document.body.appendChild(s);
      if (window.Babel) Babel.transformScriptTags();
    };
    document.body.appendChild(babelScript);
  }
})();
