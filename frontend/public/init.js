// Service worker registration + PWA install prompt handler.
// Loaded as external script (no inline JS in HTML) to satisfy strict CSP
// (script-src 'self' without 'unsafe-inline').

if ('serviceWorker' in navigator) {
  window.addEventListener('load', function() {
    navigator.serviceWorker.register('/sw.js').catch(function() {});
  });
}

window._pwaInstallPrompt = null;
window.addEventListener('beforeinstallprompt', function(e) {
  e.preventDefault();
  window._pwaInstallPrompt = e;
  document.dispatchEvent(new Event('pwa-installable'));
});

// Developer notice — only fire if Babel ACTUALLY loaded (the prod bundle failed
// and we fell back to the dev path). Previously this warned on every production
// load even when dist/app-bundle.js loaded fine, which was misleading noise.
window.addEventListener('load', function() {
  if (
    window.Babel &&
    window.location.hostname !== 'localhost' &&
    window.location.hostname !== '127.0.0.1'
  ) {
    console.warn(
      '[Signal.Trade] Babel standalone is transpiling JSX at runtime. ' +
      'This adds 2-5s TTI. Run `npm run build` and deploy dist/app-bundle.js ' +
      'to eliminate Babel from the production bundle. See build.mjs.'
    );
  }
});
