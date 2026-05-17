from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, Text, ForeignKey
from sqlalchemy.sql import func
from database import Base


class Signal(Base):
    __tablename__ = "signals"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), index=True, nullable=False)
    company = Column(String(100))
    action = Column(String(4), nullable=False)
    confidence = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    change = Column(Float, default=0)
    change_pct = Column(Float, default=0)
    entry = Column(Float, nullable=True)
    stop = Column(Float, nullable=True)
    target = Column(Float, nullable=True)
    rr = Column(String(10), nullable=True)
    headline = Column(Text, nullable=False)
    sentiment = Column(Float, default=0)
    style = Column(String(20), default="swing")
    sources = Column(JSON, default=list)
    rationale = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    is_sent = Column(Boolean, default=False)
    is_skipped = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    sent_at = Column(DateTime, nullable=True)
    notes        = Column(Text,  nullable=True)   # user journal notes
    reviewed     = Column(Boolean, default=False, nullable=False, server_default="0")
    # Engine enrichment fields — computed at scan time, stored for instant retrieval
    confidence_warning  = Column(Boolean, default=False, nullable=False, server_default="0")
    plain_english       = Column(JSON, nullable=True)     # {summary, tf_short, top_reasons}
    session             = Column(String(20), nullable=True)  # premarket | market | afterhours
    days_to_earnings    = Column(Integer, nullable=True)
    next_earnings_date  = Column(String(20), nullable=True)
    sector_etf          = Column(String(10), nullable=True)
    rs_vs_sector        = Column(Float, nullable=True)
    # Signal expiry — set at creation; nightly job deactivates past-expiry signals
    expires_at   = Column(DateTime, nullable=True)
    # Outcome tracking
    outcome_pct  = Column(Float, nullable=True)   # % return from entry after ~7 trading days
    outcome_at   = Column(DateTime, nullable=True)
    outcome_1d   = Column(Float, nullable=True)   # % return after 1 day
    outcome_3d   = Column(Float, nullable=True)   # % return after 3 days
    outcome_14d  = Column(Float, nullable=True)   # % return after 14 days
    # Trade-path analytics (filled by nightly validate_predictions run)
    hit_stop     = Column(Boolean, nullable=True)  # did price ever touch/breach the stop level
    hit_target   = Column(Boolean, nullable=True)  # did price ever touch/breach the target level
    mae          = Column(Float,   nullable=True)  # Max Adverse Excursion (worst % from entry)
    mfe          = Column(Float,   nullable=True)  # Max Favorable Excursion (best % from entry)
    exit_type    = Column(String(10), nullable=True)  # 'target' | 'stop' | 'time' | 'pending'


class SendLog(Base):
    __tablename__ = "send_log"
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(String(8))
    status = Column(String(10))
    message = Column(Text)
    created_at = Column(DateTime, server_default=func.now())



class AppSettings(Base):
    __tablename__ = "app_settings"
    id = Column(Integer, primary_key=True, default=1)
    data = Column(JSON)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class WatchlistItem(Base):
    __tablename__ = "watchlist"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), unique=True, nullable=False)
    company = Column(String(100))
    is_active = Column(Boolean, default=True)
    added_at = Column(DateTime, server_default=func.now())


class Source(Base):
    __tablename__ = "sources"
    id = Column(String(10), primary_key=True)
    name = Column(String(100))
    description = Column(Text)
    abbr = Column(String(6))
    is_on = Column(Boolean, default=True)
    requests_24h = Column(Integer, default=0)
    latency_ms = Column(Integer, default=100)
    feed = Column(String(50), default="5m")


# ── Subscription / Auth models ────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"
    id                      = Column(Integer, primary_key=True, autoincrement=True)
    email                   = Column(String(255), unique=True, nullable=False, index=True)
    password_hash           = Column(String(255), nullable=False)
    full_name               = Column(String(255), nullable=True)
    is_active               = Column(Boolean, default=True)
    is_owner                = Column(Boolean, default=False)  # bypasses all tier gates
    # Telegram link
    telegram_chat_id        = Column(String(50), nullable=True)
    telegram_link_code      = Column(String(20), nullable=True, unique=True)
    # Stripe
    stripe_customer_id      = Column(String(50), nullable=True)
    stripe_subscription_id  = Column(String(50), nullable=True)
    subscription_tier       = Column(String(20), default="free")    # free | basic | pro
    subscription_status     = Column(String(20), default="inactive") # active | inactive | past_due | canceled
    subscription_period_end = Column(DateTime, nullable=True)
    # Per-user signal preferences
    min_confidence_override = Column(Float, nullable=True)  # None = use global setting
    # Referral tracking
    referred_by             = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    referral_rewarded       = Column(Boolean, default=False)  # True = 1-month credit already applied
    # OAuth (Google SSO)
    oauth_provider          = Column(String(20), nullable=True)   # "google" | None
    oauth_sub               = Column(String(255), nullable=True, unique=True)  # Google sub ID
    # Email verification
    email_verified          = Column(Boolean, default=False, nullable=False, server_default="0")
    email_verify_token      = Column(String(64), nullable=True, unique=True, index=True)
    # Integrations — outbound webhooks + Discord delivery
    webhook_url             = Column(String(500), nullable=True)   # HMAC-signed signal POST
    discord_webhook_url     = Column(String(500), nullable=True)   # Discord channel webhook
    # Timestamps
    created_at              = Column(DateTime, server_default=func.now())
    last_seen_at            = Column(DateTime, nullable=True)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(255), nullable=False, unique=True)
    expires_at = Column(DateTime, nullable=False)
    revoked    = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())


class SignalDelivery(Base):
    """Tracks which signal was delivered to which subscriber, preventing duplicates."""
    __tablename__ = "signal_deliveries"
    id              = Column(Integer, primary_key=True, autoincrement=True)
    signal_id       = Column(Integer, ForeignKey("signals.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id         = Column(Integer, ForeignKey("users.id",   ondelete="CASCADE"), nullable=False, index=True)
    sent_at         = Column(DateTime, server_default=func.now())
    telegram_msg_id = Column(String(50), nullable=True)

class PriceAlert(Base):
    __tablename__ = "price_alerts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    target_price = Column(Float, nullable=False)
    condition = Column(String(10), default="above")  # "above" or "below"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

class PushSubscription(Base):
    __tablename__ = "push_subscriptions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    endpoint = Column(Text, nullable=False, unique=True)
    p256dh = Column(String(100), nullable=False)
    auth = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
