import hashlib
import re
import time as _time

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings

# Production security: no hardcoded fallback. JWT_SECRET must be set explicitly.
# Use: python -c "import secrets; print(secrets.token_hex(32))" to generate one.


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
    alpaca_api_secret: SecretStr = Field(default=SecretStr(""))
    auto_send_notifications: bool = True
    min_confidence: float = 40.0  # recalibrated 57→40 post phantom-win correction (2026-05-31).
    telegram_bot_token: SecretStr = Field(default=SecretStr(""))
    telegram_chat_id: str = ""
    # Scale prep: when set, signals are posted to ONE broadcast channel instead of
    # looping per-user DMs. Telegram limits bots to 30 msgs/sec; at 100+ subscribers
    # a channel post is a single API call and avoids the per-user loop entirely.
    telegram_broadcast_channel_id: str = ""

    # ── Auth ──────────────────────────────────────────────────────────────────
    jwt_secret: SecretStr = Field(default=SecretStr(""))
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60  # 60 minutes; refresh tokens (30d) handle session persistence
    refresh_token_expire_days: int = 30

    # Owner account — auto-created on first startup if set
    owner_email: str = ""
    owner_password: SecretStr = Field(default=SecretStr(""))

    @field_validator("owner_password", mode="after")
    @classmethod
    def _require_owner_password(cls, v: SecretStr) -> SecretStr:
        raw = v.get_secret_value() if hasattr(v, "get_secret_value") else str(v)
        if raw and len(raw) < 16:
            raise ValueError("OWNER_PASSWORD must be at least 16 characters when set")
        return v

    @field_validator("jwt_secret", mode="after")
    @classmethod
    def _require_jwt_secret(cls, v: SecretStr) -> SecretStr:
        raw = v.get_secret_value() if hasattr(v, "get_secret_value") else str(v)
        if raw and len(raw) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters when set")
        return v

    # ── Stripe ────────────────────────────────────────────────────────────────────
    stripe_secret_key: SecretStr = Field(default=SecretStr(""))  # sk_live_... or sk_test_...
    stripe_webhook_secret: SecretStr = Field(default=SecretStr(""))  # whsec_...
    stripe_price_basic: str = ""  # Stripe Price ID for Basic plan
    stripe_price_pro: str = ""  # Stripe Price ID for Pro plan
    app_url: str = "http://localhost:8000"  # Public URL for Stripe redirect

    # ── Google OAuth ──────────────────────────────────────────────────────────
    google_client_id: str = ""  # from Google Cloud Console → Credentials
    google_client_secret: SecretStr = Field(default=SecretStr(""))

    # ── Email (SMTP) ──────────────────────────────────────────────────────────
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: SecretStr = Field(default=SecretStr(""))
    smtp_from: str = "noreply@signal.trade"
    smtp_from_name: str = "Signal.Trade"

    # ── Monetisation / Premium APIs ───────────────────────────────────────────
    unusual_whales_api_key: str = ""
    massive_api_key: str = ""  # Massive.com API key (dark pool, options, financials)

    # Polygon (optional, but .env may contain POLYGON_API_KEY)
    polygon_api_key: str = ""

    # ── Frontend analytics sink ───────────────────────────────────────────────
    analytics_enabled: bool = True

    # ── Residual cash overlay (cash/beta parking) ───────────────────────────────
    # When enabled, the portfolio allocator auto-invests any capital not used by
    # active MR signals into a low-risk parking vehicle (default SGOV). If VIX is
    # below the threshold and the account is not in a drawdown throttle, the
    # residual can be rotated into a low-cost beta sleeve (default VOO).
    cash_overlay_enable: bool = False
    cash_overlay_ticker: str = "SGOV"  # default parking vehicle: 0-3mo T-bill ETF
    cash_overlay_beta_ticker: str = "VOO"  # optional beta sleeve: S&P 500 ETF
    cash_overlay_max_fraction: float = 0.50  # max fraction of equity in overlay
    cash_overlay_vix_threshold: float = 18.0  # VIX level below which beta sleeve is used
    cash_overlay_min_trade_dollars: float = 100.0  # minimum residual order size

    # ── Signal delivery / pipeline limits ───────────────────────────────────────
    # Cohort shadow/withheld percentages. Set both to 0 to deliver every signal.
    # Deterministic routing is preserved; changing these values re-buckets signals.
    signal_cohort_shadow_pct: int = 0
    signal_cohort_withheld_pct: int = 0
    # Long-only regime: when True, SELL signals are never delivered. When False,
    # SELLs are allowed through a mirrored MR-setup gate.
    long_only: bool = True
    # Daily send caps. 0 = no cap.
    max_sends_per_ticker_per_day: int = 1
    max_buys_per_sector_per_day: int = 2

    @model_validator(mode="after")
    def _check_cohort_pct(self):
        shadow = self.signal_cohort_shadow_pct
        withheld = self.signal_cohort_withheld_pct
        if not (0 <= shadow <= 100 and 0 <= withheld <= 100):
            raise ValueError("cohort percentages must be between 0 and 100")
        if shadow + withheld > 100:
            raise ValueError("cohort shadow + withheld percentages must not exceed 100")
        return self

    @field_validator("max_sends_per_ticker_per_day", "max_buys_per_sector_per_day")
    @classmethod
    def _non_negative_int(cls, v: int) -> int:
        if v < 0:
            raise ValueError("send caps must be non-negative")
        return v

    # Interactive Brokers Client Portal API Gateway Base URL
    ibkr_base_url: str = "https://localhost:5000/v1/api"

    # ── Event-Driven Worker Bus ───────────────────────────────────────────────
    # When set, WorkerBus uses Redis Streams instead of asyncio.Queue.
    # Enables cross-process worker distribution (separate news/fundamentals containers).
    # Format: redis://localhost:6379  or  rediss://user:pass@host:6380 (TLS)
    # Leave blank for single-process asyncio.Queue mode (default, zero dependencies).
    redis_url: str = ""

    # ── Observability ─────────────────────────────────────────────────────────
    sentry_dsn: SecretStr = Field(default=SecretStr(""))

    # ── Web Push (VAPID) ──────────────────────────────────────────────────────
    # Generate: `python -c "from py_vapid import Vapid; v=Vapid(); v.generate_keys(); print(v.private_pem().decode())"`
    vapid_private_key: SecretStr = Field(default=SecretStr(""))
    vapid_subject: str = "mailto:admin@signal.trade"

    # ── Private preview mode ───────────────────────────────────────────────────
    # When set, all HTTP requests (except health checks) require the token in a
    # ?preview_token=... query param or a preview_token cookie. Useful for
    # locking a live site to the owner while testing.
    site_private_token: SecretStr = Field(default=SecretStr(""))

    # ── Outbound delivery allowlists (SSRF prevention) ─────────────────────────
    # Comma-separated hostname suffixes. Empty = no host restriction beyond https.
    # Discord webhooks are restricted to Discord-controlled hosts by default.
    discord_allowed_hosts: str = "discord.com,discordapp.com"
    user_webhook_allowed_hosts: str = ""  # production should set explicit hosts
    push_allowed_hosts: str = ""

    @property
    def tickers(self) -> list[str]:
        return [t.strip().upper() for t in re.split(r"[,\s]+", self.watchlist) if t.strip()]

    @property
    def jwt_secret_key(self) -> str:
        """Return JWT secret. Raises in production if unset; allows dev fallback only on localhost."""
        raw = (
            self.jwt_secret.get_secret_value() if hasattr(self.jwt_secret, "get_secret_value") else str(self.jwt_secret)
        )
        if raw:
            return raw
        is_local = self.app_url.startswith("http://localhost") or self.app_url.startswith("http://127.")
        if not is_local:
            raise RuntimeError(
                "FATAL: JWT_SECRET is not set. Tokens cannot be signed securely. "
                'Generate one with: python -c "import secrets; print(secrets.token_hex(32))"'
            )
        # Dev-only: generate an ephemeral secret so uvicorn --reload works without .env setup.
        # This secret is random per process start, so reload invalidates old tokens — acceptable for dev.
        import secrets as _secrets

        return hashlib.sha256(_secrets.token_hex(32).encode()).hexdigest()

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
TIERS = ["free", "basic", "pro", "elite"]

TIER_PRICES_CENTS = {
    "free": 0,
    "basic": 1900,
    "pro": 4900,
    "elite": 9900,
}

TIER_LABELS = {
    "free": "Free",
    "basic": "Basic · $19/mo",
    "pro": "Pro · $49/mo",
    "elite": "Elite · $99/mo",
}

TIER_PLAN_FEATURES = {
    "free": [
        "3 signals/day",
        "7-day delayed history",
        "Public track record only",
        "Market context panel",
    ],
    "basic": [
        "Everything in Free",
        "Real-time signal delivery",
        "Telegram alerts",
        "Paper trading (Alpaca)",
        "Custom watchlist (50 tickers)",
        "Email alerts",
    ],
    "pro": [
        "Everything in Basic",
        "Backtest & win-rate analytics",
        "Signal correlation matrix",
        "Predictive confidence intervals",
        "Sector heatmap",
        "Simulated backtest with costs",
        "Price alerts",
        "Weekly digest",
    ],
    "elite": [
        "Everything in Pro",
        "Auto-execution (when WR > 55%)",
        "Broker integration (Alpaca/IBKR)",
        "Portfolio analytics",
        "Weekly 1-on-1 summary",
    ],
}

TIER_FEATURES = {
    "free": {"signals_view", "market_context"},
    "basic": {
        "signals_view",
        "market_context",
        "telegram",
        "backtest",
        "watchlist",
        "history",
        "chart",
        "paper_trading",  # 2026-06-18: moved from Pro to Basic as "proof before pay"
        "email_alerts",
    },
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
    },
    "elite": {
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


# ── Signal view quotas ────────────────────────────────────────────────────────
# Number of signals a user may view through /api/signals and /api/signals/history
# in a UTC day.  None = unlimited.  Owners always bypass.

SIGNAL_QUOTAS: dict[str, int | None] = {
    "free": 3,
    "basic": 100,
    "pro": None,
    "elite": None,
}


def get_quota_for_tier(tier: str, is_owner: bool = False) -> int | None:
    """Return the daily signal view limit for a tier, or None if unlimited."""
    if is_owner:
        return None
    return SIGNAL_QUOTAS.get(tier, SIGNAL_QUOTAS["free"])
