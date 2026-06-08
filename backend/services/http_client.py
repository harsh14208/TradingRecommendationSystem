"""Shared HTTP infrastructure: a cached TLS context and pooled aiohttp sessions.

Two latency bugs motivated this module:

1. ``ssl.create_default_context(cafile=certifi.where())`` was called on *every*
   outbound request (42 sites). It reads and parses the ~200 KB certifi CA
   bundle from disk synchronously — ~4.6 ms of event-loop-blocking CPU per call.
   Across a scan (hundreds of Polygon/Finnhub calls) that serialised several
   seconds of "concurrent" work. ``get_ssl_context()`` builds it once.

2. ``async with aiohttp.ClientSession() as session:`` per call meant no
   connection reuse — a fresh TCP + TLS handshake to the remote host on every
   request. ``get_session()`` returns a process-lived, per-event-loop pooled
   session so keep-alive, DNS caching, and TLS session resumption apply.
"""

import asyncio
import logging
import ssl
from contextlib import asynccontextmanager

import aiohttp
import certifi

log = logging.getLogger("signal.trade.http")

_ssl_ctx: ssl.SSLContext | None = None

# aiohttp sessions/connectors are bound to the event loop that created them, so
# we key the pool by loop. In production there is a single uvicorn loop; under
# pytest-asyncio each test loop gets (and is responsible for) its own entry.
_sessions: "dict[asyncio.AbstractEventLoop, aiohttp.ClientSession]" = {}


def get_ssl_context() -> ssl.SSLContext:
    """Return a process-wide TLS context, building it from certifi exactly once."""
    global _ssl_ctx
    if _ssl_ctx is None:
        _ssl_ctx = ssl.create_default_context(cafile=certifi.where())
    return _ssl_ctx


def get_session() -> aiohttp.ClientSession:
    """Return a pooled aiohttp session for the running loop (created on demand).

    The session must NOT be closed by callers — it lives for the loop's
    lifetime and is torn down via :func:`close_sessions` at app shutdown.
    """
    loop = asyncio.get_running_loop()
    sess = _sessions.get(loop)
    if sess is None or sess.closed:
        connector = aiohttp.TCPConnector(
            ssl=get_ssl_context(),
            limit=100,  # total concurrent connections
            limit_per_host=20,  # per remote host (Polygon, Finnhub, …)
            ttl_dns_cache=300,  # cache DNS resolutions 5 min
            keepalive_timeout=60,  # reuse idle connections for 60 s
            enable_cleanup_closed=True,
        )

        # TSYS-4d TraceConfig for provider telemetry
        async def on_request_start(session, trace_config_ctx, params):
            url_str = str(params.url).lower()
            provider = "generic"
            if "polygon" in url_str:
                provider = "polygon"
            elif "telegram" in url_str:
                provider = "telegram"
            elif "discord" in url_str:
                provider = "discord"
            elif "alpaca" in url_str:
                provider = "alpaca"
            elif "finnhub" in url_str:
                provider = "finnhub"
            trace_config_ctx.provider = provider

        async def on_request_end(session, trace_config_ctx, params):
            provider = getattr(trace_config_ctx, "provider", "generic")
            from services.provider_telemetry import record_api_call, update_quota, current_cycle_id

            cycle_id = current_cycle_id.get()
            throttled = params.response.status == 429
            record_api_call(cycle_id, provider, throttled=throttled)

            # Check for standard quota headers
            quota_rem = params.response.headers.get("X-RateLimit-Remaining") or params.response.headers.get(
                "X-Quota-Remaining"
            )
            if quota_rem is not None:
                try:
                    update_quota(cycle_id, provider, int(quota_rem))
                except Exception:
                    pass

        trace_config = aiohttp.TraceConfig()
        trace_config.on_request_start.append(on_request_start)
        trace_config.on_request_end.append(on_request_end)

        sess = aiohttp.ClientSession(connector=connector, trace_configs=[trace_config])
        _sessions[loop] = sess
    return sess


@asynccontextmanager
async def shared_session():
    """``async with`` wrapper around the pooled session that does NOT close it.

    Drop-in replacement for ``async with aiohttp.ClientSession() as session:``
    that yields the process-lived pooled session, so connections are reused
    across calls instead of being torn down on block exit.
    """
    yield get_session()


async def close_sessions() -> None:
    """Close pooled sessions. Call from the app lifespan shutdown."""
    for sess in list(_sessions.values()):
        if not sess.closed:
            try:
                await sess.close()
            except Exception as exc:  # pragma: no cover - best-effort cleanup
                log.debug("[http] session close failed: %s", exc)
    _sessions.clear()
