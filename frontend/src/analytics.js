/* ── Lightweight first-party analytics ─────────────────────────────────────
   Records CTA clicks and feature-gate events to /api/analytics/event.
   No third-party scripts, no access tokens in storage, no persistent device ID.
   Uses sendBeacon when available so navigation clicks are not lost.
   Functions are global so concatenated bundles can call them.
   -------------------------------------------------------------------------- */

(function () {
  const ENDPOINT = "/api/analytics/event";
  let _sessionId = null;

  function getSessionId() {
    if (_sessionId) return _sessionId;
    try {
      _sessionId = sessionStorage.getItem("st_analytics_session");
    } catch {}
    if (!_sessionId) {
      _sessionId = Date.now() + "-" + Math.random().toString(36).slice(2);
      try {
        sessionStorage.setItem("st_analytics_session", _sessionId);
      } catch {}
    }
    return _sessionId;
  }

  function send(payload) {
    const body = JSON.stringify(payload);
    const blob = new Blob([body], { type: "application/json" });
    if (typeof navigator !== "undefined" && navigator.sendBeacon) {
      try {
        if (navigator.sendBeacon(ENDPOINT, blob)) return;
      } catch {}
    }
    if (typeof fetch !== "undefined") {
      fetch(ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: body,
        keepalive: true,
      }).catch(function () {});
    }
  }

  window.track = function (event, properties) {
    properties = properties || {};
    send({
      event: event,
      properties: properties,
      path: typeof window !== "undefined" ? window.location.pathname + window.location.search : "",
      ts: new Date().toISOString(),
      session_id: getSessionId(),
    });
  };

  window.trackClick = function (label, extra) {
    window.track("cta_click", Object.assign({ label: label }, extra || {}));
  };

  window.trackGate = function (feature, context) {
    window.track("feature_gate", { feature: feature, context: context || "" });
  };

  window.withTracking = function (handler, label, extra) {
    return function () {
      window.trackClick(label, extra || {});
      return handler ? handler.apply(null, arguments) : undefined;
    };
  };
})();
