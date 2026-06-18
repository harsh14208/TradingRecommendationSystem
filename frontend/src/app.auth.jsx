/* global React, ReactDOM, LightweightCharts */
const { useState, useEffect, useMemo, useRef, useCallback } = React;

/* ─── Auth helpers ─────────────────────────────────────────────────────────── */
// Access token stored in module memory only — never persisted to localStorage.
// The HTTP-only refresh cookie provides persistence across page loads; the first
// 401 triggers an automatic silent refresh before retrying the original request.
let _accessToken = null;
const getToken   = () => _accessToken;
const saveToken  = t  => { _accessToken = t; };
const clearToken = () => { _accessToken = null; };

// Prevent concurrent refresh attempts from racing
let _refreshPromise = null;

async function _tryRefresh() {
  // Only one refresh at a time — subsequent callers wait for the same promise
  if (_refreshPromise) return _refreshPromise;
  _refreshPromise = fetch("/api/auth/refresh-cookie", {
    method: "POST",
    credentials: "include",   // sends the st_refresh HTTP-only cookie
    headers: { "Content-Type": "application/json" },
  })
    .then(r => r.ok ? r.json() : null)
    .then(d => {
      if (d?.access_token) { saveToken(d.access_token); return true; }
      return false;
    })
    .catch(() => false)
    .finally(() => { _refreshPromise = null; });
  return _refreshPromise;
}

async function authFetch(path, opts = {}) {
  const token = getToken();
  const headers = { "Content-Type": "application/json", ...(opts.headers || {}) };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(path, { ...opts, headers, credentials: "include" });

  if (res.status === 401) {
    // Try to silently refresh before giving up
    const refreshed = await _tryRefresh();
    if (refreshed) {
      // Retry original request with the new token
      const newToken = getToken();
      const retryHeaders = { ...headers, "Authorization": `Bearer ${newToken}` };
      return fetch(path, { ...opts, headers: retryHeaders, credentials: "include" });
    }
    // Refresh also failed — session is truly expired, send to login
    clearToken();
    window.location.replace("/login?next=/app");
  }
  return res;
}

async function apiFetch(path, opts = {}) {
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      const res = await authFetch(path, opts);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (err) {
      const isNetworkError = !err.message || !err.message.startsWith("HTTP");
      if (!isNetworkError) throw err; // 4xx/5xx — throw immediately, no retry
      if (attempt === 2) return null; // all retries exhausted
      await new Promise(r => setTimeout(r, 1000 * Math.pow(2, attempt)));
    }
  }
  return null;
}

async function apiFetchRaw(path, opts = {}) {
  // Like apiFetch but returns the raw response so callers can read headers.
  try {
    const res = await authFetch(path, opts);
    const json = res.ok ? await res.json() : null;
    return { ok: res.ok, status: res.status, json, headers: res.headers };
  } catch {
    return { ok: false, status: 0, json: null, headers: new Headers() };
  }
}
