from database import Base
from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func


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
    # Delivery-gate inputs not otherwise persisted as columns. Read by
    # eod_batch_send() so the EOD delivery path evaluates the same BUY gates as
    # the real-time path (ACT-4c: hasMr/vix/crossAssetHeadwinds/daysToExDiv).
    extra_data = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    is_sent = Column(Boolean, default=False)
    is_skipped = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    sent_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)  # user journal notes
    reviewed = Column(Boolean, default=False, nullable=False, server_default="0")
    # Engine enrichment fields — computed at scan time, stored for instant retrieval
    confidence_warning = Column(Boolean, default=False, nullable=False, server_default="0")
    plain_english = Column(JSON, nullable=True)  # {summary, tf_short, top_reasons}
    session = Column(String(20), nullable=True)  # premarket | market | afterhours
    days_to_earnings = Column(Integer, nullable=True)
    next_earnings_date = Column(String(20), nullable=True)
    sector_etf = Column(String(10), nullable=True)
    rs_vs_sector = Column(Float, nullable=True)
    # Signal expiry — set at creation; nightly job deactivates past-expiry signals
    expires_at = Column(DateTime, nullable=True)
    # Raw alpha score from _assemble_signal() — pre-heuristic, pre-haircut.
    # Stored so the live ML model can train on it without the circular dependency
    # that `confidence` creates (confidence is partially derived from the model's
    # own output via Platt scaling → training on it is tautological).
    raw_score = Column(Float, nullable=True)
    # Outcome tracking
    outcome_pct = Column(Float, nullable=True)  # % return from entry after ~7 trading days
    outcome_at = Column(DateTime, nullable=True)
    outcome_1d = Column(Float, nullable=True)  # % return after 1 day
    outcome_3d = Column(Float, nullable=True)  # % return after 3 days
    outcome_14d = Column(Float, nullable=True)  # % return after 14 days
    # Trade-path analytics (filled by nightly validate_predictions run)
    hit_stop = Column(Boolean, nullable=True)  # did price ever touch/breach the stop level
    hit_target = Column(Boolean, nullable=True)  # did price ever touch/breach the target level
    mae = Column(Float, nullable=True)  # Max Adverse Excursion (worst % from entry)
    mfe = Column(Float, nullable=True)  # Max Favorable Excursion (best % from entry)
    exit_type = Column(String(10), nullable=True)  # 'target' | 'stop' | 'time' | 'pending'


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
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_owner = Column(Boolean, default=False)  # bypasses all tier gates
    # Telegram link
    telegram_chat_id = Column(String(50), nullable=True)
    telegram_link_code = Column(String(20), nullable=True, unique=True)
    # Stripe
    stripe_customer_id = Column(String(50), nullable=True)
    stripe_subscription_id = Column(String(50), nullable=True)
    subscription_tier = Column(String(20), default="free")  # free | basic | pro
    subscription_status = Column(String(20), default="inactive")  # active | inactive | past_due | canceled
    subscription_period_end = Column(DateTime, nullable=True)
    # Per-user signal preferences
    min_confidence_override = Column(Float, nullable=True)  # None = use global setting
    # Referral tracking
    referred_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    referral_rewarded = Column(Boolean, default=False)  # True = 1-month credit already applied
    # OAuth (Google SSO)
    oauth_provider = Column(String(20), nullable=True)  # "google" | None
    oauth_sub = Column(String(255), nullable=True, unique=True)  # Google sub ID
    # Email verification
    email_verified = Column(Boolean, default=False, nullable=False, server_default="0")
    email_verify_token = Column(String(64), nullable=True, unique=True, index=True)
    # Integrations — outbound webhooks + Discord delivery
    webhook_url = Column(String(500), nullable=True)  # HMAC-signed signal POST
    discord_webhook_url = Column(String(500), nullable=True)  # Discord channel webhook
    # Autonomous execution — auto-trade signals above min confidence
    auto_execute = Column(Boolean, default=False, nullable=False, server_default="0")
    auto_execute_min_conf = Column(Float, nullable=True)  # None = use 75.0
    auto_execute_broker = Column(String(50), nullable=True)  # "alpaca" | "ibkr" | None
    auto_execute_qty_dollars = Column(Float, nullable=True)  # None = use 100.0
    # Broker credentials (Fernet-encrypted at rest)
    alpaca_key_enc = Column(Text, nullable=True)
    alpaca_secret_enc = Column(Text, nullable=True)
    alpaca_account_type = Column(String(10), nullable=True)  # "paper" | "live"
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    last_seen_at = Column(DateTime, nullable=True)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(255), nullable=False, unique=True)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())


class SignalDelivery(Base):
    """Tracks which signal was delivered to which subscriber, preventing duplicates."""

    __tablename__ = "signal_deliveries"
    id = Column(Integer, primary_key=True, autoincrement=True)
    signal_id = Column(Integer, ForeignKey("signals.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    sent_at = Column(DateTime, server_default=func.now())
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


class StripeEvent(Base):
    """Processed Stripe webhook event IDs — prevents double-processing across restarts."""

    __tablename__ = "stripe_events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(64), nullable=False, unique=True, index=True)
    processed_at = Column(DateTime, server_default=func.now())


class PasswordResetToken(Base):
    """Hashed password-reset tokens stored in DB so they survive restarts."""

    __tablename__ = "password_reset_tokens"
    id = Column(Integer, primary_key=True, autoincrement=True)
    token_hash = Column(String(64), nullable=False, unique=True, index=True)  # SHA-256 hex
    email = Column(String(255), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())


class SignalAlert(Base):
    """Per-ticker signal confidence alert rules.

    Overrides the user's global min_confidence_override for a specific ticker.
    When a signal for `ticker` is generated:
      - If the user has a matching active SignalAlert, the rule's min_confidence
        and action_filter are used instead of the global threshold.
      - action_filter "any" matches both BUY and SELL.
    """

    __tablename__ = "signal_alerts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    min_confidence = Column(Float, nullable=False)  # 0–100
    action_filter = Column(String(10), default="any")  # "BUY", "SELL", or "any"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class BrokerOrder(Base):
    """Auto-executed order placed on behalf of a user via their connected broker."""

    __tablename__ = "broker_orders"
    id = Column(Integer, primary_key=True, autoincrement=True)
    signal_id = Column(Integer, ForeignKey("signals.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    broker = Column(String(20), nullable=False)  # "alpaca"
    account_type = Column(String(10), nullable=False)  # "paper" | "live"
    alpaca_order_id = Column(String(50), nullable=True)
    symbol = Column(String(10), nullable=False, index=True)
    notional = Column(Float, nullable=False)  # dollar amount ordered
    side = Column(String(10), nullable=False)  # "buy" | "sell"
    status = Column(String(20), nullable=False, default="submitted")  # submitted | filled | rejected | error
    error_msg = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class PerformanceSnapshot(Base):
    """Immutable point-in-time record of system performance metrics.

    Written by calc_tbd_metrics.py --snapshot <tag> and automatically
    after each Sunday weekly digest. Used to track model improvements
    and detect regressions across releases.
    """

    __tablename__ = "performance_snapshots"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tag = Column(String(120), nullable=False, index=True)  # e.g. "v2-wider-atr-stops"
    git_sha = Column(String(40), nullable=True)  # HEAD at time of snapshot
    metrics = Column(JSON, nullable=False)  # full metrics dict
    n_trades = Column(Integer, nullable=False)  # quick filter without JSON parse
    win_rate = Column(Float, nullable=True)  # quick filter
    sharpe = Column(Float, nullable=True)  # quick filter
    alpha = Column(Float, nullable=True)  # Jensen's alpha annualized (quick filter)
    created_at = Column(DateTime, server_default=func.now())
