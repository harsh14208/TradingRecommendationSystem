// A8 migration 2026-05-31: esbuild bundles replace Babel CDN.
// React production builds replace dev builds. Babel removed from cache.
const CACHE = 'signal-trade-v4';
const STATIC = [
  '/',
  '/styles.css?v=3',
  '/manifest.json',
  '/dist/app-bundle.js',
  '/dist/mobile-bundle.js',
  '/dist/site-bundle.js',
  'https://unpkg.com/react@18.3.1/umd/react.production.min.js',
  'https://unpkg.com/react-dom@18.3.1/umd/react-dom.production.min.js',
  'https://unpkg.com/lightweight-charts@4/dist/lightweight-charts.standalone.production.js',
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

  // Network-first for HTML pages and JSX/JS app code so changes deploy instantly.
  // Cache-first only for immutable CDN assets (React, Babel, LightweightCharts).
  const isCDN    = url.hostname !== location.hostname;
  const isAppCode = url.pathname.endsWith('.jsx') ||
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
