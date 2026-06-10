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


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x_get_ssl_context__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_ssl_context__mutmut)
def get_ssl_context() -> ssl.SSLContext:
    """Return a process-wide TLS context, building it from certifi exactly once."""
    global _ssl_ctx
    if _ssl_ctx is None:
        _ssl_ctx = ssl.create_default_context(cafile=certifi.where())
    return _ssl_ctx


def x_get_ssl_context__mutmut_orig() -> ssl.SSLContext:
    """Return a process-wide TLS context, building it from certifi exactly once."""
    global _ssl_ctx
    if _ssl_ctx is None:
        _ssl_ctx = ssl.create_default_context(cafile=certifi.where())
    return _ssl_ctx


def x_get_ssl_context__mutmut_1() -> ssl.SSLContext:
    """Return a process-wide TLS context, building it from certifi exactly once."""
    global _ssl_ctx
    if _ssl_ctx is not None:
        _ssl_ctx = ssl.create_default_context(cafile=certifi.where())
    return _ssl_ctx


def x_get_ssl_context__mutmut_2() -> ssl.SSLContext:
    """Return a process-wide TLS context, building it from certifi exactly once."""
    global _ssl_ctx
    if _ssl_ctx is None:
        _ssl_ctx = None
    return _ssl_ctx


def x_get_ssl_context__mutmut_3() -> ssl.SSLContext:
    """Return a process-wide TLS context, building it from certifi exactly once."""
    global _ssl_ctx
    if _ssl_ctx is None:
        _ssl_ctx = ssl.create_default_context(cafile=None)
    return _ssl_ctx

mutants_x_get_ssl_context__mutmut['_mutmut_orig'] = x_get_ssl_context__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_ssl_context__mutmut['x_get_ssl_context__mutmut_1'] = x_get_ssl_context__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_ssl_context__mutmut['x_get_ssl_context__mutmut_2'] = x_get_ssl_context__mutmut_2 # type: ignore # mutmut generated
mutants_x_get_ssl_context__mutmut['x_get_ssl_context__mutmut_3'] = x_get_ssl_context__mutmut_3 # type: ignore # mutmut generated
mutants_x_get_session__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_session__mutmut)
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_orig() -> aiohttp.ClientSession:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_1() -> aiohttp.ClientSession:
    """Return a pooled aiohttp session for the running loop (created on demand).

    The session must NOT be closed by callers — it lives for the loop's
    lifetime and is torn down via :func:`close_sessions` at app shutdown.
    """
    loop = None
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_2() -> aiohttp.ClientSession:
    """Return a pooled aiohttp session for the running loop (created on demand).

    The session must NOT be closed by callers — it lives for the loop's
    lifetime and is torn down via :func:`close_sessions` at app shutdown.
    """
    loop = asyncio.get_running_loop()
    sess = None
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_3() -> aiohttp.ClientSession:
    """Return a pooled aiohttp session for the running loop (created on demand).

    The session must NOT be closed by callers — it lives for the loop's
    lifetime and is torn down via :func:`close_sessions` at app shutdown.
    """
    loop = asyncio.get_running_loop()
    sess = _sessions.get(None)
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_4() -> aiohttp.ClientSession:
    """Return a pooled aiohttp session for the running loop (created on demand).

    The session must NOT be closed by callers — it lives for the loop's
    lifetime and is torn down via :func:`close_sessions` at app shutdown.
    """
    loop = asyncio.get_running_loop()
    sess = _sessions.get(loop)
    if sess is None and sess.closed:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_5() -> aiohttp.ClientSession:
    """Return a pooled aiohttp session for the running loop (created on demand).

    The session must NOT be closed by callers — it lives for the loop's
    lifetime and is torn down via :func:`close_sessions` at app shutdown.
    """
    loop = asyncio.get_running_loop()
    sess = _sessions.get(loop)
    if sess is not None or sess.closed:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_6() -> aiohttp.ClientSession:
    """Return a pooled aiohttp session for the running loop (created on demand).

    The session must NOT be closed by callers — it lives for the loop's
    lifetime and is torn down via :func:`close_sessions` at app shutdown.
    """
    loop = asyncio.get_running_loop()
    sess = _sessions.get(loop)
    if sess is None or sess.closed:
        connector = None

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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_7() -> aiohttp.ClientSession:
    """Return a pooled aiohttp session for the running loop (created on demand).

    The session must NOT be closed by callers — it lives for the loop's
    lifetime and is torn down via :func:`close_sessions` at app shutdown.
    """
    loop = asyncio.get_running_loop()
    sess = _sessions.get(loop)
    if sess is None or sess.closed:
        connector = aiohttp.TCPConnector(
            ssl=None,
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_8() -> aiohttp.ClientSession:
    """Return a pooled aiohttp session for the running loop (created on demand).

    The session must NOT be closed by callers — it lives for the loop's
    lifetime and is torn down via :func:`close_sessions` at app shutdown.
    """
    loop = asyncio.get_running_loop()
    sess = _sessions.get(loop)
    if sess is None or sess.closed:
        connector = aiohttp.TCPConnector(
            ssl=get_ssl_context(),
            limit=None,  # total concurrent connections
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_9() -> aiohttp.ClientSession:
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
            limit_per_host=None,  # per remote host (Polygon, Finnhub, …)
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_10() -> aiohttp.ClientSession:
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
            ttl_dns_cache=None,  # cache DNS resolutions 5 min
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_11() -> aiohttp.ClientSession:
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
            keepalive_timeout=None,  # reuse idle connections for 60 s
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_12() -> aiohttp.ClientSession:
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
            enable_cleanup_closed=None,
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_13() -> aiohttp.ClientSession:
    """Return a pooled aiohttp session for the running loop (created on demand).

    The session must NOT be closed by callers — it lives for the loop's
    lifetime and is torn down via :func:`close_sessions` at app shutdown.
    """
    loop = asyncio.get_running_loop()
    sess = _sessions.get(loop)
    if sess is None or sess.closed:
        connector = aiohttp.TCPConnector(
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_14() -> aiohttp.ClientSession:
    """Return a pooled aiohttp session for the running loop (created on demand).

    The session must NOT be closed by callers — it lives for the loop's
    lifetime and is torn down via :func:`close_sessions` at app shutdown.
    """
    loop = asyncio.get_running_loop()
    sess = _sessions.get(loop)
    if sess is None or sess.closed:
        connector = aiohttp.TCPConnector(
            ssl=get_ssl_context(),
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_15() -> aiohttp.ClientSession:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_16() -> aiohttp.ClientSession:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_17() -> aiohttp.ClientSession:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_18() -> aiohttp.ClientSession:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_19() -> aiohttp.ClientSession:
    """Return a pooled aiohttp session for the running loop (created on demand).

    The session must NOT be closed by callers — it lives for the loop's
    lifetime and is torn down via :func:`close_sessions` at app shutdown.
    """
    loop = asyncio.get_running_loop()
    sess = _sessions.get(loop)
    if sess is None or sess.closed:
        connector = aiohttp.TCPConnector(
            ssl=get_ssl_context(),
            limit=101,  # total concurrent connections
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_20() -> aiohttp.ClientSession:
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
            limit_per_host=21,  # per remote host (Polygon, Finnhub, …)
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_21() -> aiohttp.ClientSession:
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
            ttl_dns_cache=301,  # cache DNS resolutions 5 min
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_22() -> aiohttp.ClientSession:
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
            keepalive_timeout=61,  # reuse idle connections for 60 s
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_23() -> aiohttp.ClientSession:
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
            enable_cleanup_closed=False,
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_24() -> aiohttp.ClientSession:
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
            url_str = None
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_25() -> aiohttp.ClientSession:
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
            url_str = str(params.url).upper()
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_26() -> aiohttp.ClientSession:
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
            url_str = str(None).lower()
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_27() -> aiohttp.ClientSession:
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
            provider = None
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_28() -> aiohttp.ClientSession:
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
            provider = "XXgenericXX"
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_29() -> aiohttp.ClientSession:
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
            provider = "GENERIC"
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_30() -> aiohttp.ClientSession:
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
            if "XXpolygonXX" in url_str:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_31() -> aiohttp.ClientSession:
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
            if "POLYGON" in url_str:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_32() -> aiohttp.ClientSession:
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
            if "polygon" not in url_str:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_33() -> aiohttp.ClientSession:
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
                provider = None
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_34() -> aiohttp.ClientSession:
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
                provider = "XXpolygonXX"
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_35() -> aiohttp.ClientSession:
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
                provider = "POLYGON"
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_36() -> aiohttp.ClientSession:
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
            elif "XXtelegramXX" in url_str:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_37() -> aiohttp.ClientSession:
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
            elif "TELEGRAM" in url_str:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_38() -> aiohttp.ClientSession:
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
            elif "telegram" not in url_str:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_39() -> aiohttp.ClientSession:
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
                provider = None
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_40() -> aiohttp.ClientSession:
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
                provider = "XXtelegramXX"
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_41() -> aiohttp.ClientSession:
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
                provider = "TELEGRAM"
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_42() -> aiohttp.ClientSession:
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
            elif "XXdiscordXX" in url_str:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_43() -> aiohttp.ClientSession:
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
            elif "DISCORD" in url_str:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_44() -> aiohttp.ClientSession:
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
            elif "discord" not in url_str:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_45() -> aiohttp.ClientSession:
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
                provider = None
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_46() -> aiohttp.ClientSession:
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
                provider = "XXdiscordXX"
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_47() -> aiohttp.ClientSession:
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
                provider = "DISCORD"
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_48() -> aiohttp.ClientSession:
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
            elif "XXalpacaXX" in url_str:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_49() -> aiohttp.ClientSession:
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
            elif "ALPACA" in url_str:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_50() -> aiohttp.ClientSession:
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
            elif "alpaca" not in url_str:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_51() -> aiohttp.ClientSession:
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
                provider = None
            elif "finnhub" in url_str:
                provider = "finnhub"
            trace_config_ctx.provider = provider

        async def on_request_end(session, trace_config_ctx, params):
            provider = getattr(trace_config_ctx, "provider", "generic")
            from services.provider_telemetry import record_api_call, update_quota, current_cycle_id

            cycle_id = current_cycle_id.get()
            throttled = params.response.status == 429
            record_api_call(cycle_id, provider, throttled=throttled)
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_52() -> aiohttp.ClientSession:
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
                provider = "XXalpacaXX"
            elif "finnhub" in url_str:
                provider = "finnhub"
            trace_config_ctx.provider = provider

        async def on_request_end(session, trace_config_ctx, params):
            provider = getattr(trace_config_ctx, "provider", "generic")
            from services.provider_telemetry import record_api_call, update_quota, current_cycle_id

            cycle_id = current_cycle_id.get()
            throttled = params.response.status == 429
            record_api_call(cycle_id, provider, throttled=throttled)
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_53() -> aiohttp.ClientSession:
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
                provider = "ALPACA"
            elif "finnhub" in url_str:
                provider = "finnhub"
            trace_config_ctx.provider = provider

        async def on_request_end(session, trace_config_ctx, params):
            provider = getattr(trace_config_ctx, "provider", "generic")
            from services.provider_telemetry import record_api_call, update_quota, current_cycle_id

            cycle_id = current_cycle_id.get()
            throttled = params.response.status == 429
            record_api_call(cycle_id, provider, throttled=throttled)
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_54() -> aiohttp.ClientSession:
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
            elif "XXfinnhubXX" in url_str:
                provider = "finnhub"
            trace_config_ctx.provider = provider

        async def on_request_end(session, trace_config_ctx, params):
            provider = getattr(trace_config_ctx, "provider", "generic")
            from services.provider_telemetry import record_api_call, update_quota, current_cycle_id

            cycle_id = current_cycle_id.get()
            throttled = params.response.status == 429
            record_api_call(cycle_id, provider, throttled=throttled)
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_55() -> aiohttp.ClientSession:
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
            elif "FINNHUB" in url_str:
                provider = "finnhub"
            trace_config_ctx.provider = provider

        async def on_request_end(session, trace_config_ctx, params):
            provider = getattr(trace_config_ctx, "provider", "generic")
            from services.provider_telemetry import record_api_call, update_quota, current_cycle_id

            cycle_id = current_cycle_id.get()
            throttled = params.response.status == 429
            record_api_call(cycle_id, provider, throttled=throttled)
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_56() -> aiohttp.ClientSession:
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
            elif "finnhub" not in url_str:
                provider = "finnhub"
            trace_config_ctx.provider = provider

        async def on_request_end(session, trace_config_ctx, params):
            provider = getattr(trace_config_ctx, "provider", "generic")
            from services.provider_telemetry import record_api_call, update_quota, current_cycle_id

            cycle_id = current_cycle_id.get()
            throttled = params.response.status == 429
            record_api_call(cycle_id, provider, throttled=throttled)
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_57() -> aiohttp.ClientSession:
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
                provider = None
            trace_config_ctx.provider = provider

        async def on_request_end(session, trace_config_ctx, params):
            provider = getattr(trace_config_ctx, "provider", "generic")
            from services.provider_telemetry import record_api_call, update_quota, current_cycle_id

            cycle_id = current_cycle_id.get()
            throttled = params.response.status == 429
            record_api_call(cycle_id, provider, throttled=throttled)
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_58() -> aiohttp.ClientSession:
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
                provider = "XXfinnhubXX"
            trace_config_ctx.provider = provider

        async def on_request_end(session, trace_config_ctx, params):
            provider = getattr(trace_config_ctx, "provider", "generic")
            from services.provider_telemetry import record_api_call, update_quota, current_cycle_id

            cycle_id = current_cycle_id.get()
            throttled = params.response.status == 429
            record_api_call(cycle_id, provider, throttled=throttled)
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_59() -> aiohttp.ClientSession:
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
                provider = "FINNHUB"
            trace_config_ctx.provider = provider

        async def on_request_end(session, trace_config_ctx, params):
            provider = getattr(trace_config_ctx, "provider", "generic")
            from services.provider_telemetry import record_api_call, update_quota, current_cycle_id

            cycle_id = current_cycle_id.get()
            throttled = params.response.status == 429
            record_api_call(cycle_id, provider, throttled=throttled)
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_60() -> aiohttp.ClientSession:
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
            trace_config_ctx.provider = None

        async def on_request_end(session, trace_config_ctx, params):
            provider = getattr(trace_config_ctx, "provider", "generic")
            from services.provider_telemetry import record_api_call, update_quota, current_cycle_id

            cycle_id = current_cycle_id.get()
            throttled = params.response.status == 429
            record_api_call(cycle_id, provider, throttled=throttled)
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_61() -> aiohttp.ClientSession:
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
            provider = None
            from services.provider_telemetry import record_api_call, update_quota, current_cycle_id

            cycle_id = current_cycle_id.get()
            throttled = params.response.status == 429
            record_api_call(cycle_id, provider, throttled=throttled)
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_62() -> aiohttp.ClientSession:
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
            provider = getattr(None, "provider", "generic")
            from services.provider_telemetry import record_api_call, update_quota, current_cycle_id

            cycle_id = current_cycle_id.get()
            throttled = params.response.status == 429
            record_api_call(cycle_id, provider, throttled=throttled)
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_63() -> aiohttp.ClientSession:
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
            provider = getattr(trace_config_ctx, None, "generic")
            from services.provider_telemetry import record_api_call, update_quota, current_cycle_id

            cycle_id = current_cycle_id.get()
            throttled = params.response.status == 429
            record_api_call(cycle_id, provider, throttled=throttled)
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_64() -> aiohttp.ClientSession:
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
            provider = getattr(trace_config_ctx, "provider", None)
            from services.provider_telemetry import record_api_call, update_quota, current_cycle_id

            cycle_id = current_cycle_id.get()
            throttled = params.response.status == 429
            record_api_call(cycle_id, provider, throttled=throttled)
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_65() -> aiohttp.ClientSession:
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
            provider = getattr("provider", "generic")
            from services.provider_telemetry import record_api_call, update_quota, current_cycle_id

            cycle_id = current_cycle_id.get()
            throttled = params.response.status == 429
            record_api_call(cycle_id, provider, throttled=throttled)
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_66() -> aiohttp.ClientSession:
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
            provider = getattr(trace_config_ctx, "generic")
            from services.provider_telemetry import record_api_call, update_quota, current_cycle_id

            cycle_id = current_cycle_id.get()
            throttled = params.response.status == 429
            record_api_call(cycle_id, provider, throttled=throttled)
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_67() -> aiohttp.ClientSession:
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
            provider = getattr(trace_config_ctx, "provider", )
            from services.provider_telemetry import record_api_call, update_quota, current_cycle_id

            cycle_id = current_cycle_id.get()
            throttled = params.response.status == 429
            record_api_call(cycle_id, provider, throttled=throttled)
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_68() -> aiohttp.ClientSession:
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
            provider = getattr(trace_config_ctx, "XXproviderXX", "generic")
            from services.provider_telemetry import record_api_call, update_quota, current_cycle_id

            cycle_id = current_cycle_id.get()
            throttled = params.response.status == 429
            record_api_call(cycle_id, provider, throttled=throttled)
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_69() -> aiohttp.ClientSession:
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
            provider = getattr(trace_config_ctx, "PROVIDER", "generic")
            from services.provider_telemetry import record_api_call, update_quota, current_cycle_id

            cycle_id = current_cycle_id.get()
            throttled = params.response.status == 429
            record_api_call(cycle_id, provider, throttled=throttled)
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_70() -> aiohttp.ClientSession:
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
            provider = getattr(trace_config_ctx, "provider", "XXgenericXX")
            from services.provider_telemetry import record_api_call, update_quota, current_cycle_id

            cycle_id = current_cycle_id.get()
            throttled = params.response.status == 429
            record_api_call(cycle_id, provider, throttled=throttled)
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_71() -> aiohttp.ClientSession:
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
            provider = getattr(trace_config_ctx, "provider", "GENERIC")
            from services.provider_telemetry import record_api_call, update_quota, current_cycle_id

            cycle_id = current_cycle_id.get()
            throttled = params.response.status == 429
            record_api_call(cycle_id, provider, throttled=throttled)
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_72() -> aiohttp.ClientSession:
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

            cycle_id = None
            throttled = params.response.status == 429
            record_api_call(cycle_id, provider, throttled=throttled)
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_73() -> aiohttp.ClientSession:
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
            throttled = None
            record_api_call(cycle_id, provider, throttled=throttled)
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_74() -> aiohttp.ClientSession:
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
            throttled = params.response.status != 429
            record_api_call(cycle_id, provider, throttled=throttled)
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_75() -> aiohttp.ClientSession:
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
            throttled = params.response.status == 430
            record_api_call(cycle_id, provider, throttled=throttled)
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_76() -> aiohttp.ClientSession:
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
            record_api_call(None, provider, throttled=throttled)
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_77() -> aiohttp.ClientSession:
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
            record_api_call(cycle_id, None, throttled=throttled)
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_78() -> aiohttp.ClientSession:
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
            record_api_call(cycle_id, provider, throttled=None)
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_79() -> aiohttp.ClientSession:
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
            record_api_call(provider, throttled=throttled)
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_80() -> aiohttp.ClientSession:
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
            record_api_call(cycle_id, throttled=throttled)
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_81() -> aiohttp.ClientSession:
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
            record_api_call(cycle_id, provider, )
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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


def x_get_session__mutmut_82() -> aiohttp.ClientSession:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc(None, provider=provider)

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


def x_get_session__mutmut_83() -> aiohttp.ClientSession:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=None)

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


def x_get_session__mutmut_84() -> aiohttp.ClientSession:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc(provider=provider)

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


def x_get_session__mutmut_85() -> aiohttp.ClientSession:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", )

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


def x_get_session__mutmut_86() -> aiohttp.ClientSession:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("XXprovider_429_totalXX", provider=provider)

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


def x_get_session__mutmut_87() -> aiohttp.ClientSession:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("PROVIDER_429_TOTAL", provider=provider)

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


def x_get_session__mutmut_88() -> aiohttp.ClientSession:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

            # Check for standard quota headers
            quota_rem = None
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


def x_get_session__mutmut_89() -> aiohttp.ClientSession:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

            # Check for standard quota headers
            quota_rem = params.response.headers.get("X-RateLimit-Remaining") and params.response.headers.get(
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


def x_get_session__mutmut_90() -> aiohttp.ClientSession:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

            # Check for standard quota headers
            quota_rem = params.response.headers.get(None) or params.response.headers.get(
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


def x_get_session__mutmut_91() -> aiohttp.ClientSession:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

            # Check for standard quota headers
            quota_rem = params.response.headers.get("XXX-RateLimit-RemainingXX") or params.response.headers.get(
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


def x_get_session__mutmut_92() -> aiohttp.ClientSession:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

            # Check for standard quota headers
            quota_rem = params.response.headers.get("x-ratelimit-remaining") or params.response.headers.get(
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


def x_get_session__mutmut_93() -> aiohttp.ClientSession:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

            # Check for standard quota headers
            quota_rem = params.response.headers.get("X-RATELIMIT-REMAINING") or params.response.headers.get(
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


def x_get_session__mutmut_94() -> aiohttp.ClientSession:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

            # Check for standard quota headers
            quota_rem = params.response.headers.get("X-RateLimit-Remaining") or params.response.headers.get(
                None
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


def x_get_session__mutmut_95() -> aiohttp.ClientSession:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

            # Check for standard quota headers
            quota_rem = params.response.headers.get("X-RateLimit-Remaining") or params.response.headers.get(
                "XXX-Quota-RemainingXX"
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


def x_get_session__mutmut_96() -> aiohttp.ClientSession:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

            # Check for standard quota headers
            quota_rem = params.response.headers.get("X-RateLimit-Remaining") or params.response.headers.get(
                "x-quota-remaining"
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


def x_get_session__mutmut_97() -> aiohttp.ClientSession:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

            # Check for standard quota headers
            quota_rem = params.response.headers.get("X-RateLimit-Remaining") or params.response.headers.get(
                "X-QUOTA-REMAINING"
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


def x_get_session__mutmut_98() -> aiohttp.ClientSession:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

            # Check for standard quota headers
            quota_rem = params.response.headers.get("X-RateLimit-Remaining") or params.response.headers.get(
                "X-Quota-Remaining"
            )
            if quota_rem is None:
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


def x_get_session__mutmut_99() -> aiohttp.ClientSession:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

            # Check for standard quota headers
            quota_rem = params.response.headers.get("X-RateLimit-Remaining") or params.response.headers.get(
                "X-Quota-Remaining"
            )
            if quota_rem is not None:
                try:
                    update_quota(None, provider, int(quota_rem))
                except Exception:
                    pass

        trace_config = aiohttp.TraceConfig()
        trace_config.on_request_start.append(on_request_start)
        trace_config.on_request_end.append(on_request_end)

        sess = aiohttp.ClientSession(connector=connector, trace_configs=[trace_config])
        _sessions[loop] = sess
    return sess


def x_get_session__mutmut_100() -> aiohttp.ClientSession:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

            # Check for standard quota headers
            quota_rem = params.response.headers.get("X-RateLimit-Remaining") or params.response.headers.get(
                "X-Quota-Remaining"
            )
            if quota_rem is not None:
                try:
                    update_quota(cycle_id, None, int(quota_rem))
                except Exception:
                    pass

        trace_config = aiohttp.TraceConfig()
        trace_config.on_request_start.append(on_request_start)
        trace_config.on_request_end.append(on_request_end)

        sess = aiohttp.ClientSession(connector=connector, trace_configs=[trace_config])
        _sessions[loop] = sess
    return sess


def x_get_session__mutmut_101() -> aiohttp.ClientSession:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

            # Check for standard quota headers
            quota_rem = params.response.headers.get("X-RateLimit-Remaining") or params.response.headers.get(
                "X-Quota-Remaining"
            )
            if quota_rem is not None:
                try:
                    update_quota(cycle_id, provider, None)
                except Exception:
                    pass

        trace_config = aiohttp.TraceConfig()
        trace_config.on_request_start.append(on_request_start)
        trace_config.on_request_end.append(on_request_end)

        sess = aiohttp.ClientSession(connector=connector, trace_configs=[trace_config])
        _sessions[loop] = sess
    return sess


def x_get_session__mutmut_102() -> aiohttp.ClientSession:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

            # Check for standard quota headers
            quota_rem = params.response.headers.get("X-RateLimit-Remaining") or params.response.headers.get(
                "X-Quota-Remaining"
            )
            if quota_rem is not None:
                try:
                    update_quota(provider, int(quota_rem))
                except Exception:
                    pass

        trace_config = aiohttp.TraceConfig()
        trace_config.on_request_start.append(on_request_start)
        trace_config.on_request_end.append(on_request_end)

        sess = aiohttp.ClientSession(connector=connector, trace_configs=[trace_config])
        _sessions[loop] = sess
    return sess


def x_get_session__mutmut_103() -> aiohttp.ClientSession:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

            # Check for standard quota headers
            quota_rem = params.response.headers.get("X-RateLimit-Remaining") or params.response.headers.get(
                "X-Quota-Remaining"
            )
            if quota_rem is not None:
                try:
                    update_quota(cycle_id, int(quota_rem))
                except Exception:
                    pass

        trace_config = aiohttp.TraceConfig()
        trace_config.on_request_start.append(on_request_start)
        trace_config.on_request_end.append(on_request_end)

        sess = aiohttp.ClientSession(connector=connector, trace_configs=[trace_config])
        _sessions[loop] = sess
    return sess


def x_get_session__mutmut_104() -> aiohttp.ClientSession:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

            # Check for standard quota headers
            quota_rem = params.response.headers.get("X-RateLimit-Remaining") or params.response.headers.get(
                "X-Quota-Remaining"
            )
            if quota_rem is not None:
                try:
                    update_quota(cycle_id, provider, )
                except Exception:
                    pass

        trace_config = aiohttp.TraceConfig()
        trace_config.on_request_start.append(on_request_start)
        trace_config.on_request_end.append(on_request_end)

        sess = aiohttp.ClientSession(connector=connector, trace_configs=[trace_config])
        _sessions[loop] = sess
    return sess


def x_get_session__mutmut_105() -> aiohttp.ClientSession:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

            # Check for standard quota headers
            quota_rem = params.response.headers.get("X-RateLimit-Remaining") or params.response.headers.get(
                "X-Quota-Remaining"
            )
            if quota_rem is not None:
                try:
                    update_quota(cycle_id, provider, int(None))
                except Exception:
                    pass

        trace_config = aiohttp.TraceConfig()
        trace_config.on_request_start.append(on_request_start)
        trace_config.on_request_end.append(on_request_end)

        sess = aiohttp.ClientSession(connector=connector, trace_configs=[trace_config])
        _sessions[loop] = sess
    return sess


def x_get_session__mutmut_106() -> aiohttp.ClientSession:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

            # Check for standard quota headers
            quota_rem = params.response.headers.get("X-RateLimit-Remaining") or params.response.headers.get(
                "X-Quota-Remaining"
            )
            if quota_rem is not None:
                try:
                    update_quota(cycle_id, provider, int(quota_rem))
                except Exception:
                    pass

        trace_config = None
        trace_config.on_request_start.append(on_request_start)
        trace_config.on_request_end.append(on_request_end)

        sess = aiohttp.ClientSession(connector=connector, trace_configs=[trace_config])
        _sessions[loop] = sess
    return sess


def x_get_session__mutmut_107() -> aiohttp.ClientSession:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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
        trace_config.on_request_start.append(None)
        trace_config.on_request_end.append(on_request_end)

        sess = aiohttp.ClientSession(connector=connector, trace_configs=[trace_config])
        _sessions[loop] = sess
    return sess


def x_get_session__mutmut_108() -> aiohttp.ClientSession:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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
        trace_config.on_request_end.append(None)

        sess = aiohttp.ClientSession(connector=connector, trace_configs=[trace_config])
        _sessions[loop] = sess
    return sess


def x_get_session__mutmut_109() -> aiohttp.ClientSession:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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

        sess = None
        _sessions[loop] = sess
    return sess


def x_get_session__mutmut_110() -> aiohttp.ClientSession:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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

        sess = aiohttp.ClientSession(connector=None, trace_configs=[trace_config])
        _sessions[loop] = sess
    return sess


def x_get_session__mutmut_111() -> aiohttp.ClientSession:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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

        sess = aiohttp.ClientSession(connector=connector, trace_configs=None)
        _sessions[loop] = sess
    return sess


def x_get_session__mutmut_112() -> aiohttp.ClientSession:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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

        sess = aiohttp.ClientSession(trace_configs=[trace_config])
        _sessions[loop] = sess
    return sess


def x_get_session__mutmut_113() -> aiohttp.ClientSession:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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

        sess = aiohttp.ClientSession(connector=connector, )
        _sessions[loop] = sess
    return sess


def x_get_session__mutmut_114() -> aiohttp.ClientSession:
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
            if throttled:
                # TSYS-10c: provider rate-limit counter for Prometheus export.
                from services.metrics import inc

                inc("provider_429_total", provider=provider)

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
        _sessions[loop] = None
    return sess

mutants_x_get_session__mutmut['_mutmut_orig'] = x_get_session__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_1'] = x_get_session__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_2'] = x_get_session__mutmut_2 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_3'] = x_get_session__mutmut_3 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_4'] = x_get_session__mutmut_4 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_5'] = x_get_session__mutmut_5 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_6'] = x_get_session__mutmut_6 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_7'] = x_get_session__mutmut_7 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_8'] = x_get_session__mutmut_8 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_9'] = x_get_session__mutmut_9 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_10'] = x_get_session__mutmut_10 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_11'] = x_get_session__mutmut_11 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_12'] = x_get_session__mutmut_12 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_13'] = x_get_session__mutmut_13 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_14'] = x_get_session__mutmut_14 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_15'] = x_get_session__mutmut_15 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_16'] = x_get_session__mutmut_16 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_17'] = x_get_session__mutmut_17 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_18'] = x_get_session__mutmut_18 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_19'] = x_get_session__mutmut_19 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_20'] = x_get_session__mutmut_20 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_21'] = x_get_session__mutmut_21 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_22'] = x_get_session__mutmut_22 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_23'] = x_get_session__mutmut_23 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_24'] = x_get_session__mutmut_24 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_25'] = x_get_session__mutmut_25 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_26'] = x_get_session__mutmut_26 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_27'] = x_get_session__mutmut_27 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_28'] = x_get_session__mutmut_28 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_29'] = x_get_session__mutmut_29 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_30'] = x_get_session__mutmut_30 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_31'] = x_get_session__mutmut_31 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_32'] = x_get_session__mutmut_32 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_33'] = x_get_session__mutmut_33 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_34'] = x_get_session__mutmut_34 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_35'] = x_get_session__mutmut_35 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_36'] = x_get_session__mutmut_36 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_37'] = x_get_session__mutmut_37 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_38'] = x_get_session__mutmut_38 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_39'] = x_get_session__mutmut_39 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_40'] = x_get_session__mutmut_40 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_41'] = x_get_session__mutmut_41 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_42'] = x_get_session__mutmut_42 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_43'] = x_get_session__mutmut_43 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_44'] = x_get_session__mutmut_44 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_45'] = x_get_session__mutmut_45 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_46'] = x_get_session__mutmut_46 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_47'] = x_get_session__mutmut_47 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_48'] = x_get_session__mutmut_48 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_49'] = x_get_session__mutmut_49 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_50'] = x_get_session__mutmut_50 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_51'] = x_get_session__mutmut_51 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_52'] = x_get_session__mutmut_52 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_53'] = x_get_session__mutmut_53 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_54'] = x_get_session__mutmut_54 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_55'] = x_get_session__mutmut_55 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_56'] = x_get_session__mutmut_56 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_57'] = x_get_session__mutmut_57 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_58'] = x_get_session__mutmut_58 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_59'] = x_get_session__mutmut_59 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_60'] = x_get_session__mutmut_60 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_61'] = x_get_session__mutmut_61 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_62'] = x_get_session__mutmut_62 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_63'] = x_get_session__mutmut_63 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_64'] = x_get_session__mutmut_64 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_65'] = x_get_session__mutmut_65 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_66'] = x_get_session__mutmut_66 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_67'] = x_get_session__mutmut_67 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_68'] = x_get_session__mutmut_68 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_69'] = x_get_session__mutmut_69 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_70'] = x_get_session__mutmut_70 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_71'] = x_get_session__mutmut_71 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_72'] = x_get_session__mutmut_72 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_73'] = x_get_session__mutmut_73 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_74'] = x_get_session__mutmut_74 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_75'] = x_get_session__mutmut_75 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_76'] = x_get_session__mutmut_76 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_77'] = x_get_session__mutmut_77 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_78'] = x_get_session__mutmut_78 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_79'] = x_get_session__mutmut_79 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_80'] = x_get_session__mutmut_80 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_81'] = x_get_session__mutmut_81 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_82'] = x_get_session__mutmut_82 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_83'] = x_get_session__mutmut_83 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_84'] = x_get_session__mutmut_84 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_85'] = x_get_session__mutmut_85 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_86'] = x_get_session__mutmut_86 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_87'] = x_get_session__mutmut_87 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_88'] = x_get_session__mutmut_88 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_89'] = x_get_session__mutmut_89 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_90'] = x_get_session__mutmut_90 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_91'] = x_get_session__mutmut_91 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_92'] = x_get_session__mutmut_92 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_93'] = x_get_session__mutmut_93 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_94'] = x_get_session__mutmut_94 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_95'] = x_get_session__mutmut_95 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_96'] = x_get_session__mutmut_96 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_97'] = x_get_session__mutmut_97 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_98'] = x_get_session__mutmut_98 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_99'] = x_get_session__mutmut_99 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_100'] = x_get_session__mutmut_100 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_101'] = x_get_session__mutmut_101 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_102'] = x_get_session__mutmut_102 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_103'] = x_get_session__mutmut_103 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_104'] = x_get_session__mutmut_104 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_105'] = x_get_session__mutmut_105 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_106'] = x_get_session__mutmut_106 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_107'] = x_get_session__mutmut_107 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_108'] = x_get_session__mutmut_108 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_109'] = x_get_session__mutmut_109 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_110'] = x_get_session__mutmut_110 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_111'] = x_get_session__mutmut_111 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_112'] = x_get_session__mutmut_112 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_113'] = x_get_session__mutmut_113 # type: ignore # mutmut generated
mutants_x_get_session__mutmut['x_get_session__mutmut_114'] = x_get_session__mutmut_114 # type: ignore # mutmut generated


@asynccontextmanager
async def shared_session():
    """``async with`` wrapper around the pooled session that does NOT close it.

    Drop-in replacement for ``async with aiohttp.ClientSession() as session:``
    that yields the process-lived pooled session, so connections are reused
    across calls instead of being torn down on block exit.
    """
    yield get_session()
mutants_x_close_sessions__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_close_sessions__mutmut)
async def close_sessions() -> None:
    """Close pooled sessions. Call from the app lifespan shutdown."""
    for sess in list(_sessions.values()):
        if not sess.closed:
            try:
                await sess.close()
            except Exception as exc:  # pragma: no cover - best-effort cleanup
                log.debug("[http] session close failed: %s", exc)
    _sessions.clear()


async def x_close_sessions__mutmut_orig() -> None:
    """Close pooled sessions. Call from the app lifespan shutdown."""
    for sess in list(_sessions.values()):
        if not sess.closed:
            try:
                await sess.close()
            except Exception as exc:  # pragma: no cover - best-effort cleanup
                log.debug("[http] session close failed: %s", exc)
    _sessions.clear()


async def x_close_sessions__mutmut_1() -> None:
    """Close pooled sessions. Call from the app lifespan shutdown."""
    for sess in list(None):
        if not sess.closed:
            try:
                await sess.close()
            except Exception as exc:  # pragma: no cover - best-effort cleanup
                log.debug("[http] session close failed: %s", exc)
    _sessions.clear()


async def x_close_sessions__mutmut_2() -> None:
    """Close pooled sessions. Call from the app lifespan shutdown."""
    for sess in list(_sessions.values()):
        if sess.closed:
            try:
                await sess.close()
            except Exception as exc:  # pragma: no cover - best-effort cleanup
                log.debug("[http] session close failed: %s", exc)
    _sessions.clear()


async def x_close_sessions__mutmut_3() -> None:
    """Close pooled sessions. Call from the app lifespan shutdown."""
    for sess in list(_sessions.values()):
        if not sess.closed:
            try:
                await sess.close()
            except Exception as exc:  # pragma: no cover - best-effort cleanup
                log.debug(None, exc)
    _sessions.clear()


async def x_close_sessions__mutmut_4() -> None:
    """Close pooled sessions. Call from the app lifespan shutdown."""
    for sess in list(_sessions.values()):
        if not sess.closed:
            try:
                await sess.close()
            except Exception as exc:  # pragma: no cover - best-effort cleanup
                log.debug("[http] session close failed: %s", None)
    _sessions.clear()


async def x_close_sessions__mutmut_5() -> None:
    """Close pooled sessions. Call from the app lifespan shutdown."""
    for sess in list(_sessions.values()):
        if not sess.closed:
            try:
                await sess.close()
            except Exception as exc:  # pragma: no cover - best-effort cleanup
                log.debug(exc)
    _sessions.clear()


async def x_close_sessions__mutmut_6() -> None:
    """Close pooled sessions. Call from the app lifespan shutdown."""
    for sess in list(_sessions.values()):
        if not sess.closed:
            try:
                await sess.close()
            except Exception as exc:  # pragma: no cover - best-effort cleanup
                log.debug("[http] session close failed: %s", )
    _sessions.clear()


async def x_close_sessions__mutmut_7() -> None:
    """Close pooled sessions. Call from the app lifespan shutdown."""
    for sess in list(_sessions.values()):
        if not sess.closed:
            try:
                await sess.close()
            except Exception as exc:  # pragma: no cover - best-effort cleanup
                log.debug("XX[http] session close failed: %sXX", exc)
    _sessions.clear()


async def x_close_sessions__mutmut_8() -> None:
    """Close pooled sessions. Call from the app lifespan shutdown."""
    for sess in list(_sessions.values()):
        if not sess.closed:
            try:
                await sess.close()
            except Exception as exc:  # pragma: no cover - best-effort cleanup
                log.debug("[HTTP] SESSION CLOSE FAILED: %S", exc)
    _sessions.clear()

mutants_x_close_sessions__mutmut['_mutmut_orig'] = x_close_sessions__mutmut_orig # type: ignore # mutmut generated
mutants_x_close_sessions__mutmut['x_close_sessions__mutmut_1'] = x_close_sessions__mutmut_1 # type: ignore # mutmut generated
mutants_x_close_sessions__mutmut['x_close_sessions__mutmut_2'] = x_close_sessions__mutmut_2 # type: ignore # mutmut generated
mutants_x_close_sessions__mutmut['x_close_sessions__mutmut_3'] = x_close_sessions__mutmut_3 # type: ignore # mutmut generated
mutants_x_close_sessions__mutmut['x_close_sessions__mutmut_4'] = x_close_sessions__mutmut_4 # type: ignore # mutmut generated
mutants_x_close_sessions__mutmut['x_close_sessions__mutmut_5'] = x_close_sessions__mutmut_5 # type: ignore # mutmut generated
mutants_x_close_sessions__mutmut['x_close_sessions__mutmut_6'] = x_close_sessions__mutmut_6 # type: ignore # mutmut generated
mutants_x_close_sessions__mutmut['x_close_sessions__mutmut_7'] = x_close_sessions__mutmut_7 # type: ignore # mutmut generated
mutants_x_close_sessions__mutmut['x_close_sessions__mutmut_8'] = x_close_sessions__mutmut_8 # type: ignore # mutmut generated
