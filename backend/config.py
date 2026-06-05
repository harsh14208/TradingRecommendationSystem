import hashlib
import time as _time

from pydantic_settings import BaseSettings

# Stable dev-only fallback — derived from a fixed seed so it survives uvicorn
# --reload (module is re-imported on each reload, but the seed stays constant).
# Tokens issued before a reload remain valid in dev.  Override with JWT_SECRET
# in .env for production (and for true token isolation between environments).
_DEV_JWT_SECRET: str = hashlib.sha256(b"signal-trade-dev-secret-v1").hexdigest()


class Settings(BaseSettings):
    # ── Existing ──────────────────────────────────────────────────────────────
    finnhub_api_key: str = ""
    watchlist: str = "NVDA,TSLA,AAPL,AMD,META,MSFT,PLTR,SMCI,QQQ,SPY,IWM,GLD,XLK,XLF,XLE"
    scan_interval: int = 60  # legacy fallback, unused
    scan_times: str = ""  # legacy fixed-slot override (leave empty for continuous mode)
    # Continuous market-hours scanning: fire every N minutes from 09:30 to 16:00 ET.
    # Set to 0 to fall back to legacy scan_times fixed slots.
    scan_interval_min: int = 15
    fred_api_key: str = ""
    alpaca_api_key: str = ""
    alpaca_api_secret: str = ""
    auto_send_notifications: bool = True
    min_confidence: float = 40.0  # recalibrated 57→40 post phantom-win correction (2026-05-31).
    # Old 57% = phantom-win scale where "57%" → real WR ~42%. After correction all signals
    # cluster at ~42% honest confidence. 40% floor preserves positive-EV filter:
    # 42.5% WR × 1.63× payoff = +EV. Swing floor (70%) and position floor (0%) unchanged.
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    # Scale prep: when set, signals are posted to ONE broadcast channel instead of
    # looping per-user DMs. Telegram limits bots to 30 msgs/sec; at 100+ subscribers
    # a channel post is a single API call and avoids the per-user loop entirely.
    telegram_broadcast_channel_id: str = ""

    # ── Auth ──────────────────────────────────────────────────────────────────
    jwt_secret: str = ""  # set in .env — MUST be a long random string
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60  # 60 minutes; refresh tokens (30d) handle session persistence
    refresh_token_expire_days: int = 30

    # Owner account — auto-created on first startup if set
    owner_email: str = ""
    owner_password: str = ""

    # ── Stripe ────────────────────────────────────────────────────────────────
    stripe_secret_key: str = ""  # sk_live_... or sk_test_...
    stripe_webhook_secret: str = ""  # whsec_...
    stripe_price_basic: str = ""  # Stripe Price ID for Basic plan
    stripe_price_pro: str = ""  # Stripe Price ID for Pro plan
    app_url: str = "http://localhost:8000"  # Public URL for Stripe redirect

    # ── Google OAuth ──────────────────────────────────────────────────────────
    google_client_id: str = ""  # from Google Cloud Console → Credentials
    google_client_secret: str = ""  # from Google Cloud Console → Credentials

    # ── Discord OAuth ─────────────────────────────────────────────────────────
    discord_client_id: str = ""  # from discord.com/developers/applications → OAuth2
    discord_client_secret: str = ""  # from discord.com/developers/applications → OAuth2

    # ── Email (SMTP) ──────────────────────────────────────────────────────────
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "noreply@signal.trade"
    smtp_from_name: str = "Signal.Trade"

    # ── Monetisation / Premium APIs ───────────────────────────────────────────
    unusual_whales_api_key: str = ""
    massive_api_key: str = ""  # Massive.com API key (dark pool, options, financials)

    # Polygon (optional, but .env may contain POLYGON_API_KEY)
    polygon_api_key: str = ""

    # ── Event-Driven Worker Bus ───────────────────────────────────────────────
    # When set, WorkerBus uses Redis Streams instead of asyncio.Queue.
    # Enables cross-process worker distribution (separate news/fundamentals containers).
    # Format: redis://localhost:6379  or  rediss://user:pass@host:6380 (TLS)
    # Leave blank for single-process asyncio.Queue mode (default, zero dependencies).
    redis_url: str = ""

    # ── Web Push (VAPID) ──────────────────────────────────────────────────────
    # Generate: `python -c "from py_vapid import Vapid; v=Vapid(); v.generate_keys(); print(v.private_pem().decode())"`
    vapid_private_key: str = ""
    vapid_subject: str = "mailto:admin@signal.trade"

    @property
    def tickers(self) -> list[str]:
        return [t.strip().upper() for t in self.watchlist.split(",") if t.strip()]

    @property
    def jwt_secret_key(self) -> str:
        """Return JWT secret; use a stable random one in dev if not set in .env."""
        return self.jwt_secret or _DEV_JWT_SECRET

    model_config = {"env_file": ".env", "case_sensitive": False, "extra": "ignore"}


_settings_cache: Settings | None = None
_settings_ts: float = 0.0
_SETTINGS_TTL = 30.0


def get_settings() -> Settings:
    global _settings_cache, _settings_ts
    now = _time.monotonic()
    if _settings_cache is None or now - _settings_ts > _SETTINGS_TTL:
        _settings_cache = Settings()
        _settings_ts = now
    return _settings_cache


# Tier hierarchy — higher index = more access
TIERS = ["free", "basic", "pro"]

TIER_PRICES_CENTS = {
    "free": 0,
    "basic": 2900,
    "pro": 7900,
}

TIER_LABELS = {
    "free": "Free",
    "basic": "Basic · $29/mo",
    "pro": "Pro · $79/mo",
}

TIER_PLAN_FEATURES = {
    "free": [
        "View signals in dashboard",
        "Market context panel",
        "Signal history (read-only)",
    ],
    "basic": [
        "Everything in Free",
        "Telegram signal delivery",
        "Backtest & win-rate stats",
        "Custom watchlist",
        "Full signal history",
    ],
    "pro": [
        "Everything in Basic",
        "Paper trading (Alpaca)",
        "Signal correlation matrix",
        "Predictive confidence intervals",
        "Sector heatmap",
        "Simulated backtest with costs",
        "Price alerts",
        "Weekly digest",
    ],
}

TIER_FEATURES = {
    "free": {"signals_view", "market_context"},
    "basic": {"signals_view", "market_context", "telegram", "backtest", "watchlist", "history", "chart"},
    "pro": {
        "signals_view",
        "market_context",
        "telegram",
        "backtest",
        "watchlist",
        "history",
        "chart",
        "paper_trading",
        "correlation",
        "predictive",
        "price_alerts",
        "sector_heatmap",
        "backtest_simulate",
        "weekly_digest",
        "auto_execute",
        "broker_orders",
    },
}


def has_feature(tier: str, feature: str, is_owner: bool = False) -> bool:
    if is_owner:
        return True
    return feature in TIER_FEATURES.get(tier, set())


def tier_gte(tier: str, min_tier: str) -> bool:
    return TIERS.index(tier) >= TIERS.index(min_tier)
