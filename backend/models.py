from database import Base
from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.sql import func


class Signal(Base):
    __tablename__ = "signals"
    __table_args__ = (CheckConstraint("action IN ('BUY', 'SELL')", name="ck_signal_action"),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), index=True, nullable=False)
    company = Column(String(100))
    action = Column(String(4), nullable=False)
    confidence = Column(Float, nullable=False)
    raw_confidence = Column(Float, nullable=True)
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
    is_active = Column(Boolean, default=True, nullable=False, server_default="1")
    is_sent = Column(Boolean, default=False, index=True, nullable=False, server_default="0")  # TSYS-12c: hot filter
    is_skipped = Column(Boolean, default=False, nullable=False, server_default="0")
    skip_reason = Column(Text, nullable=True)  # delivery-gate skip reason (Item 7)
    created_at = Column(DateTime, server_default=func.now(), index=True)
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
    # Options VRP engine payload (additive, nullable; see services/options_engine.py)
    option_strategy = Column(
        String(30), nullable=True
    )  # SELL_CASH_SEC_PUT | SELL_STRANGLE | SELL_DEFINED_RISK | LONG_STRADDLE
    option_legs = Column(JSON, nullable=True)  # [{side, option_symbol, quantity, strike, expiry, premium, position}]
    option_underlying_action = Column(String(10), nullable=True)  # directional signal action on the underlying
    option_richness = Column(Float, nullable=True)  # implied / forecast move
    option_impl_move = Column(Float, nullable=True)  # option-implied horizon move (fraction)
    option_forecast_move = Column(Float, nullable=True)  # model-forecast horizon move (fraction)
    option_exp_gain = Column(Float, nullable=True)  # expected P&L ($)
    option_max_loss = Column(Float, nullable=True)  # tail-capped max loss ($)
    option_days_to_earnings = Column(Integer, nullable=True)

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
    cycle_id = Column(String(100), nullable=True, index=True)  # TSYS-4b
    policy_version = Column(String(20), nullable=True)  # TSYS-6c


class SendLog(Base):
    __tablename__ = "send_log"
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(String(8))
    status = Column(String(10))
    message = Column(Text)
    chat_id = Column(String(50), nullable=True)  # DISC-3: actual recipient chat_id
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    cycle_id = Column(String(100), nullable=True, index=True)  # TSYS-4b


class AppSettings(Base):
    __tablename__ = "app_settings"
    id = Column(Integer, primary_key=True, autoincrement=True, default=1)
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
    __table_args__ = (
        CheckConstraint("subscription_tier IN ('free', 'basic', 'pro', 'elite')", name="ck_user_subscription_tier"),
        CheckConstraint("options_mode IN ('none', 'signal', 'paper', 'live')", name="ck_user_options_mode"),
    )
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
    subscription_tier = Column(
        String(20), default="free", nullable=False, server_default="free"
    )  # free | basic | pro | elite
    subscription_status = Column(
        String(20), default="inactive", nullable=False, server_default="inactive"
    )  # active | inactive | past_due | canceled
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
    webhook_secret = Column(String(255), nullable=True)  # TSYS-3d HMAC webhook signing secret
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
    # Billing — trial abuse gating
    trial_consumed_at = Column(DateTime, nullable=True)
    # Lockout & Security
    failed_login_attempts = Column(Integer, default=0, nullable=False, server_default="0")
    lockout_until = Column(DateTime, nullable=True)
    # Risk limits (TSYS-9b)
    max_daily_orders = Column(Integer, nullable=True)
    max_daily_loss = Column(Float, nullable=True)
    max_open_positions = Column(Integer, nullable=True)
    max_ticker_notional = Column(Float, nullable=True)
    max_sector_exposure = Column(Float, nullable=True)
    # Encryption key versioning (TSYS-9d)
    alpaca_key_version = Column(Integer, default=1, nullable=False, server_default="1")
    # Risk acknowledgement (TSYS-13b)
    risk_acknowledged = Column(Boolean, default=False, nullable=False, server_default="0")
    risk_acknowledged_at = Column(DateTime, nullable=True)
    # Options execution mode & risk settings (default signal-only)
    options_mode = Column(
        String(10), default="signal", nullable=False, server_default="signal"
    )  # none | signal | paper | live
    options_capital = Column(Float, nullable=True)  # defaults to global DEFAULT_CAPITAL if null
    options_risk_per_trade = Column(Float, nullable=True)  # fraction of capital
    options_max_book_risk = Column(Float, nullable=True)  # fraction of capital
    options_max_positions = Column(Integer, nullable=True)
    options_max_iv_sell = Column(Float, nullable=True)  # e.g. 0.80


class UserSignalQuota(Base):
    """Tracks how many signals a user has viewed in the current UTC day."""

    __tablename__ = "user_signal_quotas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    window_start = Column(DateTime, nullable=False)  # UTC midnight of current window
    views_count = Column(Integer, default=0, nullable=False, server_default="0")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(255), nullable=False, unique=True)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)
    user_agent = Column(String(255), nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class SignalDelivery(Base):
    """Tracks which signal or system message was delivered to which subscriber (TSYS-3a)."""

    __tablename__ = "signal_deliveries"
    id = Column(Integer, primary_key=True, autoincrement=True)
    signal_id = Column(Integer, ForeignKey("signals.id", ondelete="CASCADE"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    channel = Column(String(20), nullable=False, default="telegram", server_default="telegram")
    status = Column(String(20), nullable=False, default="sent", server_default="sent")
    retry_count = Column(Integer, default=0, nullable=False, server_default="0")
    latency_ms = Column(Float, nullable=True)
    error_code = Column(String(50), nullable=True)
    dedupe_key = Column(String(150), nullable=True, unique=True, index=True)
    telegram_msg_id = Column(String(50), nullable=True)
    provider_message_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())  # DISC-7: when the row was created
    sent_at = Column(DateTime, nullable=True)  # when delivery was confirmed (may differ from created_at)
    cycle_id = Column(String(100), nullable=True, index=True)  # TSYS-4b


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
    customer_id = Column(String(64), nullable=True)
    subscription_id = Column(String(64), nullable=True)
    event_type = Column(String(64), nullable=True)
    transition = Column(String(100), nullable=True)
    handler_result = Column(Text, nullable=True)
    is_replay = Column(Boolean, default=False, nullable=False, server_default="0")
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
    __table_args__ = (
        CheckConstraint(
            "status IN ('submitted','filled','rejected','error','orphan','canceled')",
            name="ck_broker_order_status",
        ),
        UniqueConstraint("alpaca_order_id", name="uq_broker_orders_alpaca_order_id"),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    signal_id = Column(Integer, ForeignKey("signals.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    broker = Column(String(20), nullable=False)  # "alpaca"
    account_type = Column(String(10), nullable=False)  # "paper" | "live"
    alpaca_order_id = Column(String(50), nullable=True)
    symbol = Column(String(24), nullable=False, index=True)  # TSYS-14: OCC option symbols are ~21 chars
    notional = Column(Float, nullable=False)  # dollar amount ordered
    side = Column(String(10), nullable=False)  # "buy" | "sell"
    status = Column(
        String(20), nullable=False, default="submitted", server_default="submitted", index=True
    )  # TSYS-12c: submitted | filled | rejected | error | orphan | canceled
    error_msg = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    cycle_id = Column(String(100), nullable=True, index=True)  # TSYS-4b

    # Live fill ledger columns (QENG-3a)
    arrival_price = Column(Float, nullable=True)
    nbbo_mid = Column(Float, nullable=True)
    spread = Column(Float, nullable=True)
    route_order_type = Column(String(50), nullable=True)  # "market" | "limit" | "midpoint"
    requested_qty = Column(Float, nullable=True)
    filled_qty = Column(Float, nullable=True)
    avg_fill_price = Column(Float, nullable=True)
    partial_fills = Column(JSON, nullable=True)  # list of sub-fills
    fees = Column(Float, nullable=True)
    reject_reason = Column(Text, nullable=True)
    stop_child_order_id = Column(String(50), nullable=True)
    target_child_order_id = Column(String(50), nullable=True)
    final_execution_status = Column(String(20), nullable=True)


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


# ── Quant-engine lifecycle (additive, normalized) ─────────────────────────────
#
# A proper quant-engine spine layered ADDITIVELY on top of the existing
# signal-delivery schema. These tables reference existing rows (`signals`,
# `broker_orders`, `users`) by id and never modify those tables:
#
#   instruments ─┬─< bars                 (point-in-time market data)
#                ├─< feature_snapshots     (point-in-time alpha features ← signals)
#                ├─< fills                 (execution ledger ← broker_orders)
#                └─< positions ─< (accounting unit ← signals)
#   users ───────┬─< positions
#                ├─< pnl_daily             (equity curve / drawdown)
#                └─< risk_metrics          (portfolio beta / VaR / concentration)
#
# Lifecycle: instruments → signals → broker_orders → fills → positions →
#            pnl_daily / risk_metrics.


class Instrument(Base):
    """Securities master — one row per tradable symbol (sector, ADV, beta, …)."""

    __tablename__ = "instruments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(12), unique=True, nullable=False, index=True)
    name = Column(String(120), nullable=True)
    asset_type = Column(String(16), nullable=False, default="equity", server_default="equity")
    sector = Column(String(40), nullable=True)
    industry = Column(String(80), nullable=True)
    sector_etf = Column(String(10), nullable=True)  # XLK, XLF, XLE, …
    currency = Column(String(3), nullable=False, default="USD", server_default="USD")
    market_cap = Column(Float, nullable=True)  # USD
    adv_usd = Column(Float, nullable=True)  # 30-day average daily $ volume
    beta = Column(Float, nullable=True)  # vs SPY
    shares_outstanding = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, server_default="1")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Bar(Base):
    """OHLCV time-series bar — point-in-time market data (one row per symbol/interval/ts)."""

    __tablename__ = "bars"
    id = Column(Integer, primary_key=True, autoincrement=True)
    instrument_id = Column(Integer, ForeignKey("instruments.id", ondelete="CASCADE"), nullable=False)
    interval = Column(String(4), nullable=False, default="1d", server_default="1d")  # 1d | 1h | 5m | 1w
    ts = Column(DateTime, nullable=False)  # close-of-period timestamp (UTC)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False, default=0, server_default="0")
    vwap = Column(Float, nullable=True)
    __table_args__ = (
        UniqueConstraint("instrument_id", "interval", "ts", name="uq_bars_instrument_interval_ts"),
        Index("ix_bars_instrument_ts", "instrument_id", "ts"),
    )


class FeatureSnapshot(Base):
    """Point-in-time feature vector for an instrument, optionally tied to the signal it fed.

    Lets a delivered signal's exact inputs be reproduced with no look-ahead. Hot
    scalars are first-class indexed columns; the full vector lives in `features`.
    """

    __tablename__ = "feature_snapshots"
    id = Column(Integer, primary_key=True, autoincrement=True)
    instrument_id = Column(Integer, ForeignKey("instruments.id", ondelete="CASCADE"), nullable=False)
    signal_id = Column(Integer, ForeignKey("signals.id", ondelete="SET NULL"), nullable=True, index=True)
    ts = Column(DateTime, nullable=False)  # observation time
    rsi = Column(Float, nullable=True)
    bb_pct_b = Column(Float, nullable=True)
    ibs = Column(Float, nullable=True)
    vwap_pct = Column(Float, nullable=True)
    atr_pct = Column(Float, nullable=True)
    zscore = Column(Float, nullable=True)
    quality_score = Column(Float, nullable=True)
    features = Column(JSON, nullable=True)  # full point-in-time feature dict
    effective_time = Column(DateTime, nullable=True)  # when the feature vector became effective
    provider_timestamp = Column(DateTime, nullable=True)  # timestamp from provider
    provider = Column(String(50), nullable=True)  # provider name
    feature_vector_hash = Column(String(64), nullable=True, index=True)  # hash of feature vector
    signal_policy_version = Column(String(20), nullable=True, index=True)  # active policy version
    created_at = Column(DateTime, server_default=func.now())
    __table_args__ = (Index("ix_feature_snapshots_instrument_ts", "instrument_id", "ts"),)


class Fill(Base):
    """Individual execution against a broker order (an order may fill in parts)."""

    __tablename__ = "fills"
    __table_args__ = (UniqueConstraint("broker_fill_id", name="uq_fills_broker_fill_id"),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    broker_order_id = Column(Integer, ForeignKey("broker_orders.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    instrument_id = Column(Integer, ForeignKey("instruments.id", ondelete="SET NULL"), nullable=True, index=True)
    side = Column(String(4), nullable=False)  # buy | sell
    qty = Column(Float, nullable=False)  # shares filled
    price = Column(Float, nullable=False)  # fill price
    commission = Column(Float, nullable=False, default=0, server_default="0")
    slippage_bps = Column(Float, nullable=True)  # vs signal arrival/entry price
    broker_fill_id = Column(String(64), nullable=True)
    filled_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)


class Position(Base):
    """Open or closed position for a user in an instrument — the accounting unit."""

    __tablename__ = "positions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    instrument_id = Column(Integer, ForeignKey("instruments.id", ondelete="CASCADE"), nullable=False, index=True)
    signal_id = Column(Integer, ForeignKey("signals.id", ondelete="SET NULL"), nullable=True, index=True)
    status = Column(String(8), nullable=False, default="open", server_default="open")  # open | closed
    side = Column(String(5), nullable=False, default="long", server_default="long")  # long | short
    qty = Column(Float, nullable=False, default=0, server_default="0")
    avg_entry_price = Column(Float, nullable=False)
    avg_exit_price = Column(Float, nullable=True)
    cost_basis = Column(Float, nullable=False, default=0, server_default="0")  # qty * avg_entry_price
    last_price = Column(Float, nullable=True)  # latest mark
    market_value = Column(Float, nullable=True)
    unrealized_pnl = Column(Float, nullable=True)
    realized_pnl = Column(Float, nullable=False, default=0, server_default="0")
    stop = Column(Float, nullable=True)
    target = Column(Float, nullable=True)
    opened_at = Column(DateTime, server_default=func.now(), index=True)
    closed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    __table_args__ = (Index("ix_positions_user_status", "user_id", "status"),)


class PnlDaily(Base):
    """Daily portfolio P&L mark per user — equity curve, exposure, drawdown."""

    __tablename__ = "pnl_daily"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    date = Column(Date, nullable=False)
    equity = Column(Float, nullable=False, default=0, server_default="0")  # total account equity
    cash = Column(Float, nullable=True)
    realized_pnl = Column(Float, nullable=False, default=0, server_default="0")  # realized that day
    unrealized_pnl = Column(Float, nullable=False, default=0, server_default="0")
    gross_exposure = Column(Float, nullable=True)  # Σ |position market value|
    net_exposure = Column(Float, nullable=True)  # Σ signed market value
    drawdown_pct = Column(Float, nullable=True)  # from running peak equity
    n_positions = Column(Integer, nullable=False, default=0, server_default="0")
    created_at = Column(DateTime, server_default=func.now())
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_pnl_daily_user_date"),)


class RiskMetric(Base):
    """Daily portfolio risk snapshot per user — beta, vol, VaR, concentration."""

    __tablename__ = "risk_metrics"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    date = Column(Date, nullable=False)
    portfolio_beta = Column(Float, nullable=True)  # vs SPY
    portfolio_vol = Column(Float, nullable=True)  # annualized
    var_95 = Column(Float, nullable=True)  # 1-day 95% VaR
    max_sector_pct = Column(Float, nullable=True)  # largest sector weight
    avg_pairwise_corr = Column(Float, nullable=True)  # §83 cross-signal correlation
    gross_leverage = Column(Float, nullable=True)
    net_leverage = Column(Float, nullable=True)
    metrics = Column(JSON, nullable=True)  # extensible overflow
    created_at = Column(DateTime, server_default=func.now())
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_risk_metrics_user_date"),)


class OAuthState(Base):
    __tablename__ = "oauth_states"
    state = Column(String(64), primary_key=True, index=True)
    referred_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    code_challenge = Column(String(255), nullable=True)
    code_verifier = Column(String(255), nullable=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class OAuthOneTimeCode(Base):
    __tablename__ = "oauth_one_time_codes"
    code = Column(String(64), primary_key=True, index=True)
    access_token = Column(String(500), nullable=False)
    user_data = Column(JSON, nullable=False)  # stores user_dict
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class EmailChangeRequest(Base):
    __tablename__ = "email_change_requests"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    old_email = Column(String(255), nullable=False)
    new_email = Column(String(255), nullable=False)
    token_hash = Column(String(64), nullable=False, unique=True, index=True)  # SHA-256 hex
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class AuthAuditLog(Base):
    __tablename__ = "auth_audit_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    email = Column(String(255), nullable=False, index=True)
    event = Column(String(50), nullable=False)  # "failed_login", "lockout", "unlock", "password_reset_fail"
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class BackgroundJobRun(Base):
    """Tracks background job execution history (TSYS-4a)."""

    __tablename__ = "background_job_runs"
    __table_args__ = (UniqueConstraint("job_name", "digest_week", name="uq_background_job_runs_weekly_digest_week"),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_name = Column(String(100), nullable=False)
    cycle_id = Column(String(100), nullable=True, index=True)
    start_time = Column(DateTime, nullable=False, server_default=func.now())
    end_time = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=False, default="running")  # running | completed | failed
    duration_s = Column(Float, nullable=True)
    error = Column(Text, nullable=True)
    worker_id = Column(String(100), nullable=True)
    digest_week = Column(String(10), nullable=True, index=True)


class ProviderTelemetry(Base):
    """Tracks API provider budget and usage telemetry per scan cycle (TSYS-4d)."""

    __tablename__ = "provider_telemetry"
    id = Column(Integer, primary_key=True, autoincrement=True)
    cycle_id = Column(String(100), nullable=False, index=True)
    provider = Column(String(50), nullable=False)  # "polygon", "alpaca", "yfinance", etc.
    api_calls = Column(Integer, default=0, nullable=False)
    cache_hits = Column(Integer, default=0, nullable=False)
    cache_misses = Column(Integer, default=0, nullable=False)
    quota_remaining = Column(Integer, nullable=True)
    throttles = Column(Integer, default=0, nullable=False)
    fallback_usage = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


# ── TSYS-5 Reliability models ──────────────────────────────────────────────────


class ProviderResponseSample(Base):
    """Raw vendor responses sampled for schema-drift detection and replay (TSYS-5b)."""

    __tablename__ = "provider_response_samples"
    id = Column(Integer, primary_key=True, autoincrement=True)
    provider = Column(String(50), nullable=False)
    endpoint = Column(String(255), nullable=False)
    ticker = Column(String(12), nullable=True)
    status_code = Column(Integer, nullable=False)
    latency_ms = Column(Float, nullable=True)
    response_body = Column(Text, nullable=False)
    is_drifted = Column(Boolean, default=False, nullable=False, server_default="0")
    drift_details = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)  # TSYS-12c: retention purge


class ProviderHealthScorecard(Base):
    """Provider health metrics scorecard per endpoint (TSYS-5a)."""

    __tablename__ = "provider_health_scorecards"
    __table_args__ = (UniqueConstraint("provider", "endpoint", name="uq_provider_endpoint"),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    provider = Column(String(50), nullable=False)
    endpoint = Column(String(255), nullable=False)
    latency_avg_ms = Column(Float, default=0.0, nullable=False, server_default="0.0")
    error_rate = Column(Float, default=0.0, nullable=False, server_default="0.0")
    stale_data_rate = Column(Float, default=0.0, nullable=False, server_default="0.0")
    schema_drift_count = Column(Integer, default=0, nullable=False, server_default="0")
    health_score = Column(Float, default=100.0, nullable=False, server_default="100.0")
    is_active = Column(Boolean, default=True, nullable=False, server_default="1")
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())


class ShortVolumeDaily(Base):
    """Daily FINRA short-volume alt-data from Polygon (/stocks/v1/short-volume).

    Backfilled + reused as an orthogonal-to-OHLCV positioning signal:
    short_volume_ratio = short-marked % of consolidated daily volume. History ~2024-02+.
    """

    __tablename__ = "short_volume_daily"
    __table_args__ = (
        UniqueConstraint("ticker", "date", name="uq_short_volume_ticker_date"),
        Index("ix_short_volume_ticker_date", "ticker", "date"),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(12), nullable=False)
    date = Column(Date, nullable=False)
    short_volume_ratio = Column(Float, nullable=True)  # percent (0-100)
    short_volume = Column(Integer, nullable=True)
    total_volume = Column(Integer, nullable=True)
    fetched_at = Column(DateTime, server_default=func.now())


class ShortInterestBiweekly(Base):
    """Bi-weekly FINRA short-interest alt-data from Polygon (/stocks/v1/short-interest).

    Orthogonal to OHLCV and to daily short-volume: ``short_interest`` is the aggregate
    settled short position (shares); ``days_to_cover`` = short_interest / avg_daily_volume
    is the squeeze-fuel metric. ``date`` is the FINRA settlement_date. History ~2017-12+.
    """

    __tablename__ = "short_interest_biweekly"
    __table_args__ = (
        UniqueConstraint("ticker", "date", name="uq_short_interest_ticker_date"),
        Index("ix_short_interest_ticker_date", "ticker", "date"),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(12), nullable=False)
    date = Column(Date, nullable=False)  # FINRA settlement_date
    short_interest = Column(Integer, nullable=True)  # shares short
    days_to_cover = Column(Float, nullable=True)  # short_interest / avg_daily_volume
    avg_daily_volume = Column(Integer, nullable=True)
    fetched_at = Column(DateTime, server_default=func.now())


class OptionsChainDaily(Base):
    """§110 — nightly CBOE delayed-quotes options chain snapshot per ticker.

    Accumulates live-only option metrics so the engine can build a self-grown
    IV-rank / skew / PCR history for tickers without paying for historical
    options data. Contract-level detail is kept in ``contracts_snapshot`` but
    the primary signals are pre-aggregated for fast reads.
    """

    __tablename__ = "options_chain_daily"
    __table_args__ = (
        UniqueConstraint("ticker", "date", name="uq_options_chain_ticker_date"),
        Index("ix_options_chain_ticker_date", "ticker", "date"),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(12), nullable=False)
    date = Column(Date, nullable=False)
    contract_count = Column(Integer, nullable=True)
    put_call_ratio = Column(Float, nullable=True)
    total_volume = Column(Integer, nullable=True)
    total_open_interest = Column(Integer, nullable=True)
    avg_iv = Column(Float, nullable=True)
    near_iv = Column(Float, nullable=True)
    far_iv = Column(Float, nullable=True)
    iv_term_spike = Column(Float, nullable=True)
    iv_rank = Column(Float, nullable=True)
    skew_25d = Column(Float, nullable=True)
    max_pain = Column(Float, nullable=True)
    net_gex = Column(Float, nullable=True)  # $-denominated net gamma exposure
    spot = Column(Float, nullable=True)
    source = Column(String(20), nullable=True, server_default="cboe")
    contracts_snapshot = Column(JSON, nullable=True)  # list of normalized contracts
    fetched_at = Column(DateTime, server_default=func.now())


class OratsDailyFeatures(Base):
    """§111 — ORATS historical near-EOD options features per ticker per day.

    Persisted because the purchased ORATS FTP download expires after ~30 days.
    This table becomes the long-term source for backtests and research; the
    raw CSVs and parquet cache are only build-time artifacts.
    """

    __tablename__ = "orats_daily_features"
    __table_args__ = (
        UniqueConstraint("ticker", "date", name="uq_orats_daily_features_ticker_date"),
        Index("ix_orats_daily_features_ticker_date", "ticker", "date"),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(12), nullable=False)
    date = Column(Date, nullable=False)
    stk_px = Column(Float, nullable=True)
    atm_iv_30d = Column(Float, nullable=True)
    iv_25d_call = Column(Float, nullable=True)
    iv_25d_put = Column(Float, nullable=True)
    pc_iv_skew = Column(Float, nullable=True)
    gex = Column(Float, nullable=True)
    dex = Column(Float, nullable=True)
    pc_volume_ratio = Column(Float, nullable=True)
    pc_oi_ratio = Column(Float, nullable=True)
    total_opt_volume = Column(Float, nullable=True)
    total_opt_oi = Column(Float, nullable=True)
    zero_dte_put_volume = Column(Float, nullable=True)
    iv_rank_252 = Column(Float, nullable=True)
    iv_pctile_252 = Column(Float, nullable=True)
    fetched_at = Column(DateTime, server_default=func.now())


class CorporateActionValidation(Base):
    """Validation comparing corporate-action adjustments across providers (TSYS-5c)."""

    __tablename__ = "corporate_action_validations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(12), nullable=False)
    action_type = Column(String(20), nullable=False)  # "split" | "dividend"
    execution_date = Column(Date, nullable=False)
    polygon_value = Column(Float, nullable=True)
    yfinance_value = Column(Float, nullable=True)
    is_valid = Column(Boolean, default=True, nullable=False, server_default="1")
    discrepancy_details = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


# ── TSYS-6 Signal Engine Explainability models ───────────────────────────────


class SignalGateTrace(Base):
    """Machine-readable gate trace for every generated signal (TSYS-6a)."""

    __tablename__ = "signal_gate_traces"
    id = Column(Integer, primary_key=True, autoincrement=True)
    signal_id = Column(Integer, ForeignKey("signals.id", ondelete="CASCADE"), nullable=False, index=True)
    gate_id = Column(String(50), nullable=False)
    version = Column(String(20), nullable=False)
    input_values = Column(JSON, nullable=True)
    score_delta = Column(Float, default=0.0, nullable=False, server_default="0.0")
    confidence_delta = Column(Float, default=0.0, nullable=False, server_default="0.0")
    passed = Column(Boolean, nullable=False)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class GateRegistry(Base):
    """Registry of technical signal/scoring gates (TSYS-6b)."""

    __tablename__ = "gate_registry"
    id = Column(String(50), primary_key=True)
    owner = Column(String(100), nullable=False)
    status = Column(String(20), default="active", nullable=False, server_default="active")
    test_coverage = Column(Float, default=0.0, nullable=False, server_default="0.0")
    live_validation_status = Column(String(50), nullable=True)
    retirement_criteria = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class SignalPolicy(Base):
    """Signal generation policy snapshots (TSYS-6c)."""

    __tablename__ = "signal_policies"
    version = Column(String(20), primary_key=True)
    config = Column(JSON, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


# ── TSYS-7 Calibration & ML Ops models ────────────────────────────────────────


class ModelRegistry(Base):
    """Model registry tracking trained/deployed ML models (TSYS-7a)."""

    __tablename__ = "model_registry"
    model_id = Column(String(100), primary_key=True)
    training_data_hash = Column(String(64), nullable=False)
    feature_schema_hash = Column(String(64), nullable=False)
    hyperparameters = Column(JSON, nullable=True)
    metrics = Column(JSON, nullable=True)
    approval_decision = Column(String(20), default="pending", nullable=False, server_default="pending")
    is_active = Column(Boolean, default=False, nullable=False, server_default="0")
    created_at = Column(DateTime, server_default=func.now())


class ModelShadowScore(Base):
    """Champion/challenger model shadow scoring logs (TSYS-7c)."""

    __tablename__ = "model_shadow_scores"
    id = Column(Integer, primary_key=True, autoincrement=True)
    signal_id = Column(Integer, ForeignKey("signals.id", ondelete="CASCADE"), nullable=False, index=True)
    model_id = Column(String(100), nullable=False)
    score = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    champion_score = Column(Float, nullable=False)
    champion_confidence = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class CalibrationHistory(Base):
    """Preserves historical calibration curves for rollback capability (TSYS-7d)."""

    __tablename__ = "calibration_history"
    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(String(20), nullable=False)
    calibration_data = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=False, nullable=False, server_default="0")
    created_at = Column(DateTime, server_default=func.now())


# ── TSYS-8 Outcomes & Backtests models ────────────────────────────────────────


class OutcomeResolverAudit(Base):
    """Audit records of prediction resolution passes (TSYS-8a)."""

    __tablename__ = "outcome_resolver_audits"
    id = Column(Integer, primary_key=True, autoincrement=True)
    run_at = Column(DateTime, server_default=func.now())
    signals_processed = Column(Integer, default=0, nullable=False, server_default="0")
    signals_resolved = Column(Integer, default=0, nullable=False, server_default="0")
    price_source = Column(String(50), nullable=True)
    missing_bars_count = Column(Integer, default=0, nullable=False, server_default="0")
    corrections_applied = Column(JSON, nullable=True)
    unresolved_reasons = Column(JSON, nullable=True)


class OutcomePathSnapshot(Base):
    """Point-in-time price path snapshots for MAE/MFE replay (TSYS-8b)."""

    __tablename__ = "outcome_path_snapshots"
    id = Column(Integer, primary_key=True, autoincrement=True)
    signal_id = Column(Integer, ForeignKey("signals.id", ondelete="CASCADE"), nullable=False, index=True)
    path_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


# ── TSYS-10 Observability models ──────────────────────────────────────────────


class IncidentTimeline(Base):
    """System incident audit timeline (TSYS-10a)."""

    __tablename__ = "incident_timeline"
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String(50), nullable=False)
    severity = Column(String(10), default="info", nullable=False, server_default="info")
    message = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


# ── TSYS-12 Data Retention models ─────────────────────────────────────────────


class DataRetentionRule(Base):
    """Data retention and anonymization rules configuration (TSYS-12b)."""

    __tablename__ = "data_retention_rules"
    table_name = Column(String(100), primary_key=True)
    retention_days = Column(Integer, nullable=False)
    anonymize = Column(Boolean, default=False, nullable=False, server_default="0")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


# ── TSYS-13 Safety & CCPA models ──────────────────────────────────────────────


class ActionAuditLog(Base):
    """Immutable log of safety-critical admin and user actions (TSYS-13c)."""

    __tablename__ = "action_audit_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(100), nullable=False)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, server_default=func.now())


# ── QENG Quant Engine models ──────────────────────────────────────────────────


class ResearchExperiment(Base):
    """Research experiment registry (QENG-1a)."""

    __tablename__ = "research_experiments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    experiment_type = Column(
        String(50), nullable=False, index=True
    )  # "screener" | "parameter_sweep" | "gate_ablation" | "ml_training" | "factor_mining"
    hypothesis = Column(Text, nullable=False)
    universe = Column(JSON, nullable=True)  # list of tickers or description
    data_version = Column(String(50), nullable=False)
    git_sha = Column(String(40), nullable=True)
    search_space = Column(JSON, nullable=True)
    number_of_trials = Column(Integer, default=1, nullable=False)
    is_metrics = Column(JSON, nullable=True)
    oos_metrics = Column(JSON, nullable=True)
    dsr_pbo = Column(JSON, nullable=True)  # e.g., {"dsr": 0.25, "pbo": 0.05}
    sprt_params = Column(JSON, nullable=True)  # §99: {"h0": 0, "h1": 1.0, "alpha": 0.05, "beta": 0.05}
    sprt_state = Column(JSON, nullable=True)  # §99: {"llr": 0.0, "n": 0, "decision": "continue"}
    decision = Column(
        String(20), default="pending", nullable=False, index=True
    )  # "promoted" | "rejected" | "shadow" | "pending"
    promotion_status = Column(
        String(20), default="pending", nullable=False, index=True
    )  # "pending" | "live" | "rolled_back" | "expired"
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
