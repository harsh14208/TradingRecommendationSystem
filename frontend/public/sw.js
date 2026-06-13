// A8 migration 2026-05-31: esbuild bundles replace Babel CDN.
// React production builds replace dev builds. Babel removed from cache.
//
// v5 (2026-06-12): only same-origin, always-available URLs are precached.
// Precaching cross-origin CDN scripts (unpkg) made cache.addAll() REJECT under
// the strict CSP connect-src — which failed the whole install, so the new SW
// never activated and users were stuck on a stale cached bundle. App code
// (bundles, CSS, HTML) is now network-first so deploys land immediately; the
// CDN libs are cached opportunistically on first fetch instead.
const CACHE = 'signal-trade-v5';
const STATIC = [
  '/',
  '/manifest.json',
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(STATIC)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);

  // Never intercept cross-origin requests (React/LightweightCharts on unpkg,
  // Google Fonts, Cloudflare beacon). The page CSP restricts the SW's own
  // fetch() via connect-src, so intercepting them makes fetch() throw and we'd
  // serve the HTML fallback in place of the script — which is exactly what
  // broke React with "MIME type ('text/html') is not executable". Let the
  // browser load these directly under script-src/font-src.
  if (url.origin !== location.origin) return;

  // Always go network-first for API calls
  if (url.pathname.startsWith('/api/') || url.pathname.startsWith('/ws')) {
    e.respondWith(
      fetch(e.request).catch(() =>
        new Response(JSON.stringify({ error: 'offline' }), {
          headers: { 'Content-Type': 'application/json' }
        })
      )
    );
    return;
  }

  // Network-first for ALL same-origin app code (HTML, the esbuild bundles, CSS,
  // JSX) so a redeploy lands immediately instead of being pinned to a stale
  // cached bundle. Cache-first only for immutable cross-origin CDN libs.
  const isCDN    = url.hostname !== location.hostname;
  const isAppCode = url.pathname.endsWith('.jsx') ||
                    url.pathname.endsWith('.js') ||
                    url.pathname.endsWith('.css') ||
                    url.pathname.endsWith('.html') ||
                    url.pathname === '/app' ||
                    url.pathname === '/' ||
                    url.pathname === '/login' ||
                    url.pathname === '/signup';

  if (isAppCode && !isCDN) {
    // Network-first: always try server, fall back to cache only if offline
    e.respondWith(
      fetch(e.request).then(resp => {
        if (resp && resp.status === 200 && e.request.method === 'GET') {
          const clone = resp.clone();
          caches.open(CACHE).then(c => c.put(e.request, clone));
        }
        return resp;
      }).catch(() => caches.match(e.request))
    );
    return;
  }

  // Cache-first for CDN assets and other static resources
  e.respondWith(
    caches.match(e.request).then(cached => {
      if (cached) return cached;
      return fetch(e.request).then(resp => {
        if (resp && resp.status === 200 && e.request.method === 'GET') {
          const clone = resp.clone();
          caches.open(CACHE).then(c => c.put(e.request, clone));
        }
        return resp;
      }).catch(() => caches.match('/'));
    })
  );
});

// Push notification handler
self.addEventListener('push', e => {
  const data = e.data?.json() ?? {};
  e.waitUntil(
    self.registration.showNotification(data.title || 'Signal.Trade', {
      body:  data.body  || '',
      tag:   data.tag   || 'signal',
      icon:  '/manifest.json',
      badge: '/manifest.json',
    })
  );
});

self.addEventListener('notificationclick', e => {
  e.notification.close();
  e.waitUntil(clients.openWindow('/'));
});
