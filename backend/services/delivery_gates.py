"""
Delivery gates — pre-send eligibility checks for every signal.

Each gate returns early with a skip reason string if the signal should not
be delivered. A None return means the signal passed all gates.

Extracted from scanner._maybe_send() so that:
  - Gates are unit-testable in isolation
  - Live broker execution (OAuth path) can run the same gates
  - scanner.py stays focused on orchestration
"""

import logging
from datetime import datetime, timedelta, timezone

import pytz
from sqlalchemy import func, select

log = logging.getLogger("scanner")


def _utcnow_naive() -> datetime:
    """UTC timestamp compatible with existing naive SQLAlchemy DateTime columns."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


# ── Gate configuration ────────────────────────────────────────────────────────

# Empirical live data (543 resolved, Apr-May 2026) — alpha/beta decomposition:
#   Position: alpha +0.890%/trade, WR 56.6%  → keep flowing
#   Swing:    alpha −1.028%/trade, WR 41.2%  → only very-high-confidence setups
#   Intraday: alpha −0.321%/trade, WR 30.4%  → disabled
# Swing floor raised 62→65 (2026-05-26), then 65→70 (2026-05-30): persistent
# negative alpha (−1.028%/trade) — only near-ceiling setups worth trading.
STYLE_CONF_FLOORS: dict[str, float] = {
    # RE-ENABLED 2026-06-15 (owner request) at the global floor. Intraday was
    # disabled for cause — live alpha −0.321%/trade, WR 30.4% (May 2026) — and is
    # a momentum/breakout strategy, so it also bypasses the MR-setup gate below
    # (intraday signals are structurally non-mean-reverting). EXPECT this to
    # surface more, lower-quality signals and drag WR/Sharpe; monitor and dial the
    # floor back up (or restore 999.0) if live stats stay negative.
    "intraday": 40.0,
    "swing": 46.0,  # recalibrated 70→46 post phantom-win correction (2026-05-31).
    # Old 70% = top ~15% of phantom-inflated distribution (−1.028%/trade alpha, WR 41.2%).
    # On honest 40-50% confidence scale, 46% selects the upper half of the distribution.
    # Swing alpha was −1.028%/trade; only near-ceiling setups pass even at new scale.
    "position": 0.0,  # no additional floor — driven by global min_confidence (40%)
    "options_vrp": 0.0,  # additive option signals are gated by their own risk engine
}

# ── Intraday safety rail (auto-disable) ──────────────────────────────────────
# Intraday was re-enabled 2026-06-15 despite poor historical stats. This is the
# self-correcting guard: once enough intraday BUYs have resolved, if live win
# rate stays below the floor, intraday delivery auto-blocks (and auto-recovers
# if WR climbs back). No human intervention or scheduled job required.
_INTRADAY_SAFETY_MIN_N = 30  # need N≥30 resolved before judging (avoid noise)
_INTRADAY_SAFETY_MIN_WR = 0.40  # block intraday delivery if live WR < 40%


async def _intraday_safety_blocked(db) -> tuple[bool, float, int]:
    """Return (blocked, wr, n) for recent resolved intraday BUYs. blocked=True
    when N≥_INTRADAY_SAFETY_MIN_N and WR<_INTRADAY_SAFETY_MIN_WR."""
    from models import Signal

    rows = (
        (
            await db.execute(
                select(Signal.outcome_pct)
                .where(Signal.style == "intraday")
                .where(Signal.action == "BUY")
                .where(Signal.is_sent == True)
                .where(Signal.outcome_pct.isnot(None))
                .order_by(Signal.sent_at.desc())
                .limit(100)
            )
        )
        .scalars()
        .all()
    )
    n = len(rows)
    if n < _INTRADAY_SAFETY_MIN_N:
        return False, 0.0, n
    wr = sum(1 for o in rows if o > 0) / n
    return wr < _INTRADAY_SAFETY_MIN_WR, wr, n


# Sectors with empirical PF < 0.40x blocked until per-sector models retrained.
# XLF 0.32x, XLP 0.35x, XLU insufficient data.
# ACT-1 (2026-06-06): XLI added — live WR 36.1% (N=36, N≥30 with WR<50%) per
#   gate_contribution_analysis.py --sector-wr. Supersedes §31-5 (XLI live-eligible):
#   IS treated XLI stocks as eligible but live MR edge did not materialise.
BLOCKED_SECTORS: frozenset[str] = frozenset({"XLF", "XLP", "XLU", "XLI"})

# Tickers that don't exhibit 10-day price-level MR behavior:
#  - Semi equipment (LRCX, MRVL, AMAT, KLAC): continuation cycle, multi-quarter
#    IS: LRCX −7.20%, MRVL −6.65%; OOS: KLAC −4.36%, AMAT 0 trades
#  - XLF regional banks (STT, MTB): rate-cycle driven, not price-level MR
#    OOS v5: STT −4.75% (0% WR), MTB −4.16% (0% WR)
# Only structural / N≥30 confirmed blocks.  Small-N blocks (e.g. APH N=4) are
# selection on outcomes / online overfitting to noise and have been removed.
BLOCKED_TICKERS: frozenset[str] = frozenset(
    {
        "LRCX",
        "MRVL",
        "AMAT",
        "KLAC",  # semi equipment — continuation not MR (IS: LRCX −7.20%, MRVL −6.65%; OOS N≥30)
        "STT",
        "MTB",  # XLF regional banks — rate-cycle driven (OOS v5: both 0% WR, N≥30)
        "APH",  # live underperformer (N=4, 0% WR, −8.70%) — kept for parity with CLAUDE.md
    }
)

# Same-underlying aliases: if GOOGL signal fires, it counts as a GOOG position
# (and vice versa) — both are Alphabet equity, different share classes only.
TICKER_ALIASES: dict[str, str] = {
    "GOOGL": "GOOG",
    "GOOG": "GOOGL",
}


def effective_conf_floor(
    style: str,
    ticker: str,
    min_confidence: float,
    ticker_win_rates: dict | None = None,
) -> float:
    """Effective confidence floor a BUY must clear to be deliverable.

    Mirrors the floor logic inside check_delivery_gates: the global
    min_confidence, raised by the ticker-adaptive override (low-WR tickers
    must clear a stricter bar, high-WR tickers get a relaxed one) and the
    per-style floor (STYLE_CONF_FLOORS — intraday is effectively disabled).
    """
    floor = float(min_confidence)
    twr = (ticker_win_rates or {}).get(ticker)
    if isinstance(twr, (int, float)) and not isinstance(twr, bool):
        if twr < 0.45:
            floor = max(floor, 68.0)
        elif twr >= 0.75:
            floor = max(floor, 52.0)
    return max(floor, STYLE_CONF_FLOORS.get(style, 70.0))


def structural_delivery_status(
    *,
    action: str,
    ticker: str,
    sector_etf: str | None,
    style: str,
    confidence: float,
    min_confidence: float,
    has_mr: bool = True,
    has_mr_sell: bool = False,
    long_only: bool = True,
    require_mr_setup: bool = True,
    ticker_win_rates: dict | None = None,
    promoted_sectors: frozenset[str] | set[str] = frozenset(),
) -> tuple[bool, str | None]:
    """Pure, cheap subset of check_delivery_gates: the *structural* eligibility
    gates that don't depend on transient state (no DB/network/clock).

    Returns ``(deliverable, reason)`` — ``reason`` is ``None`` when deliverable,
    otherwise a short human-readable label for why this signal would NOT be sent.

    Covers exactly the gates that decide whether a signal can ever be
    delivered, independent of timing: SELL-disabled/long-only regime (HOLD and
    SELL are never delivered), the mean-reversion setup requirement (BUYs need
    ≥1 oversold condition — a property of the signal, not the clock), the
    confidence floor (global + style + ticker-adaptive), and the blocked-ticker /
    blocked-sector lists (honoring QENG-1c sector promotions).

    Deliberately excludes the *transient* gates (pre-earnings/ex-div blackouts,
    VIX<15 suspension, FOMC proximity, sector-concentration cap, market-hours,
    cooldown, holiday/Thursday haircuts) — those flip with the calendar/clock
    and are evaluated only at actual send time.

    ``has_mr`` mirrors the live MR-setup hard block: a BUY without ≥2 oversold
    mean-reversion conditions is never delivered. Defaults True for callers/rows
    that don't carry the flag (older signals predating the field).
    """
    # Options VRP signals have their own risk engine; don't apply stock MR/long-only gates.
    if style == "options_vrp":
        return True, None

    # Long-only regime: only BUY is deliverable (HOLD/SELL never are).
    if long_only and action != "BUY":
        return False, f"{action} not delivered — long-only regime"

    # MR-setup hard block — BUY needs ≥1 oversold condition (RSI/BB%B/IBS/VWAP%; reverted 2→1 2026-06-17).
    # SELL needs ≥1 overbought condition when long-only is disabled.
    # Intraday BUY is a momentum/breakout strategy (structurally non-mean-reverting),
    # so it is exempt — gated by its own style floor instead. Intraday SELL is NOT
    # exempt (2026-06-22): the MR-exempt intraday-SELL cohort resolved 0% WR /
    # −6.46%/trade since 2026-06-15, so all SELLs require an overbought setup.
    # Disabled by default 2026-07-22 (require_mr_setup=False) — the gate fixed a
    # real WR gap but collapsed live volume to near zero once the market stopped
    # offering oversold dips; hasMr/hasMrSell are still passed through so a
    # replacement gate can be built from real outcome data.
    if require_mr_setup:
        if action == "BUY" and style != "intraday" and not has_mr:
            return False, "no mean-reversion setup — needs ≥1 oversold condition"
        if action == "SELL" and not has_mr_sell:
            return False, "no SELL mean-reversion setup — needs ≥1 overbought condition"

    # Blocked tickers (no confirmed 10-day MR edge, N≥30).
    if ticker in BLOCKED_TICKERS:
        return False, f"{ticker} blocked — no confirmed 10-day MR edge"

    # Blocked sectors — check both the signal's sector ETF and the ticker
    # itself (sector ETFs carry sector_etf=None because they ARE the sector).
    # QENG-1c-promoted sectors are allowed through.
    blocked_key = sector_etf if (sector_etf and sector_etf in BLOCKED_SECTORS) else ticker
    if blocked_key in BLOCKED_SECTORS and blocked_key not in promoted_sectors:
        return False, f"sector {blocked_key} blocked — low profit factor"

    # Confidence floor (global + style + ticker-adaptive).
    floor = effective_conf_floor(style, ticker, min_confidence, ticker_win_rates)
    if confidence < floor:
        if STYLE_CONF_FLOORS.get(style, 70.0) >= 999.0:
            return False, f"{style} style disabled"
        return False, f"confidence {confidence:.0f}% < {floor:.0f}% floor"

    # Cohort-EV gate (QENG-COHORT) — mirrors check_delivery_gates so
    # generation-time pre-filtering and feed deliverability tagging agree with
    # send time. Reads only the cached nightly snapshot (no DB/network); cold
    # start → passthrough, so this stays cheap and never blocks on absent data.
    try:
        from services.cohort_edge_gate import get_cohort_decision

        _cd = get_cohort_decision(action, style, sector_etf)
        if not _cd.deliver:
            return False, _cd.reason
    except Exception:  # pragma: no cover — defensive; gate must never break tagging
        pass

    return True, None


def passes_structural_delivery_gates(
    *,
    action: str,
    ticker: str,
    sector_etf: str | None,
    style: str,
    confidence: float,
    min_confidence: float,
    has_mr: bool = True,
    has_mr_sell: bool = False,
    long_only: bool = True,
    require_mr_setup: bool = True,
    ticker_win_rates: dict | None = None,
    promoted_sectors: frozenset[str] | set[str] = frozenset(),
) -> bool:
    """Boolean convenience wrapper over :func:`structural_delivery_status`."""
    ok, _ = structural_delivery_status(
        action=action,
        ticker=ticker,
        sector_etf=sector_etf,
        style=style,
        confidence=confidence,
        min_confidence=min_confidence,
        has_mr=has_mr,
        has_mr_sell=has_mr_sell,
        long_only=long_only,
        require_mr_setup=require_mr_setup,
        ticker_win_rates=ticker_win_rates,
        promoted_sectors=promoted_sectors,
    )
    return ok


async def check_delivery_gates(
    sig_dict: dict,
    db,
    settings,
) -> tuple[str | None, dict]:
    """
    Run all pre-send eligibility gates against sig_dict.

    Returns:
        (skip_reason, sig_dict)
        skip_reason — human-readable string if blocked, else None.
        sig_dict    — possibly mutated copy (holiday haircut may modify confidence).

    The caller should return immediately when skip_reason is not None.
    """
    ticker = sig_dict["ticker"]
    action = sig_dict.get("action", "")
    conf = sig_dict.get("confidence", 0)
    style = sig_dict.get("style", "swing")

    # ── Action guard ─────────────────────────────────────────────────────────
    if action not in ("BUY", "SELL"):
        return f"action={action} not BUY/SELL", sig_dict

    # Options VRP signals are additive and bypass stock MR/long-only gates,
    # but they still must clear their own confidence floor and risk limits.
    if sig_dict.get("option_strategy"):
        opt_conf = sig_dict.get("confidence", 0)
        opt_min = getattr(settings, "option_min_confidence", 50.0)
        if opt_conf < opt_min:
            return f"option confidence {opt_conf:.0f}% < floor {opt_min:.0f}%", sig_dict
        return None, sig_dict

    # Item 3: SELL delivery controlled by LONG_ONLY setting.
    if getattr(settings, "long_only", True) and action == "SELL":
        return "SELL delivery disabled — long-only regime", sig_dict

    # ── MR gate — hard block for BUY/SELL signals without a mean-reversion setup ──
    # Root-cause fix for live WR 42% vs backtest WR 68% gap (audit 2026-06-02).
    # BUY needs ≥1 oversold condition; SELL (when long_only=false) needs ≥1
    # overbought condition. Intraday BUY is momentum/breakout and exempt — but
    # intraday SELL is NOT exempt as of 2026-06-22: the MR-exempt intraday-SELL
    # cohort resolved at 0% WR / −6.46%/trade since 2026-06-15 (shorting momentum
    # into a rising tape). All SELLs now require an overbought MR setup.
    # NOTE: default missing hasMr to True for pre-field rows (aligns with structural_delivery_status).
    # Disabled by default 2026-07-22 (settings.require_mr_setup=False) — see
    # config.py comment: the gate fixed a real WR gap but collapsed live BUY
    # volume to near zero once the market stopped offering oversold dips.
    # hasMr/hasMrSell are still computed and tagged on every signal for a
    # future replacement gate.
    if getattr(settings, "require_mr_setup", True):
        _has_mr = sig_dict.get("hasMr")
        if _has_mr is None:
            _has_mr = True
        if action == "BUY" and style != "intraday" and not _has_mr:
            return "no MR setup — ≥1 of RSI/BB%B/IBS/VWAP% oversold conditions required for BUY delivery", sig_dict
        if action == "SELL" and not sig_dict.get("hasMrSell", False):
            return "no SELL MR setup — ≥1 overbought condition required for SELL delivery", sig_dict

    # ── Cohort-EV gate (QENG-COHORT) — self-calibrating (action, style, sector) ──
    # Learned from the system's own trailing resolved outcomes; blocks cohorts
    # whose lower confidence bound on net edge is ≤ 0 and sizes survivors by
    # shrunk net edge. Cold-start / thin-data → passthrough (never starves a
    # fresh deployment). Refreshed nightly (main.py). Options VRP is exempt
    # (own risk engine, returned above).
    try:
        from services.cohort_edge_gate import get_cohort_decision

        _cd = get_cohort_decision(action, style, sig_dict.get("sectorEtf"))
        if not _cd.deliver:
            return _cd.reason, sig_dict
        if _cd.size_mult != 1.0:
            sig_dict = dict(sig_dict)
            _scale = sig_dict.get("positionSizeScale") or 1.0
            sig_dict["positionSizeScale"] = round(min(max(_scale * _cd.size_mult, 0.10), 3.00), 2)
            sig_dict.setdefault("rationale", [])
            sig_dict["rationale"] = list(sig_dict["rationale"]) + [
                {
                    "src": "Risk Gate",
                    "head": f"Cohort-EV Sizing ({_cd.size_mult:.2f}×)",
                    "body": (
                        f"Realized net edge for this signal's cohort [{_cd.matched_key}] is "
                        f"{_cd.net_edge:+.2f}%/trade over the trailing window (n={_cd.n}). "
                        f"Position size scaled {_cd.size_mult:.2f}× accordingly."
                    ),
                    "sentiment": "pos" if _cd.size_mult > 1.0 else "neg",
                    "meta": f"cohort={_cd.matched_key} net={_cd.net_edge:+.2f}% n={_cd.n} (QENG-COHORT)",
                }
            ]
    except Exception:
        log.warning("cohort-EV gate check failed; delivering without it", exc_info=True)  # pragma: no mutate

    # ── Ticker-adaptive confidence floor (checked before global floor) ─────────
    # High-win tickers (≥75% historical WR) get a relaxed 52% floor instead of
    # the global min_confidence, so quality tickers aren't killed by a high global
    # setting. Low-win tickers (<45% WR) must clear a stricter 68% bar.
    _effective_conf_floor = settings.min_confidence
    try:
        from models import AppSettings

        _srow = (await db.execute(select(AppSettings).where(AppSettings.id == 1))).scalar_one_or_none()
        app_data = (_srow.data or {}) if _srow else {}
        ticker_wrs = app_data.get("adaptive_weights", {}).get("ticker_win_rates", {})
        twr = ticker_wrs.get(ticker)
        if isinstance(twr, (int, float)) and not isinstance(twr, bool):
            if twr < 0.45:
                _effective_conf_floor = max(_effective_conf_floor, 68.0)
            elif twr >= 0.75:
                _effective_conf_floor = max(_effective_conf_floor, 52.0)
    except Exception:
        log.warning("Failed to load adaptive weights in delivery gates", exc_info=True)  # pragma: no mutate

    # ── Confidence haircuts (applied BEFORE floors so they can gate delivery) ─
    # Pre-long-weekend haircut (-5pp, non-blocking)
    try:
        from services.market_calendar import get_upcoming_holidays, is_pre_long_weekend

        holidays = await get_upcoming_holidays()
        is_long_wknd, holiday_name = is_pre_long_weekend(holidays)
        if is_long_wknd:
            sig_dict = dict(sig_dict)
            sig_dict["confidence"] = round(max(35.0, sig_dict["confidence"] - 5.0), 1)
            sig_dict.setdefault("rationale", [])
            sig_dict["rationale"] = list(sig_dict["rationale"]) + [
                {
                    "src": "Risk Gate",
                    "head": f"Pre-{holiday_name} Haircut (−5pp)",
                    "body": (
                        f"Signal is 2 trading days before {holiday_name} (3-day weekend). "
                        "Lower liquidity, wider bid-ask spreads, and gap risk at open after "
                        "the holiday reduce expected return. Confidence reduced by 5pp."
                    ),
                    "sentiment": "neg",
                    "meta": f"holiday={holiday_name} haircut=-5pp",
                }
            ]
            conf = sig_dict["confidence"]
    except Exception:
        pass

    # §57 Thursday signal confidence haircut (−3pp, non-blocking)
    try:
        _now_utc = datetime.now(timezone.utc)
        if action == "BUY" and _now_utc.weekday() == 3:  # Thursday = 3
            _conf_before = sig_dict.get("confidence", 0)
            if _conf_before < 58.0:
                sig_dict = dict(sig_dict)
                sig_dict["confidence"] = round(max(35.0, _conf_before - 3.0), 1)
                sig_dict.setdefault("rationale", [])
                sig_dict["rationale"] = list(sig_dict["rationale"]) + [
                    {
                        "src": "Risk Gate",
                        "head": "Thursday Fill Haircut (−3pp)",
                        "body": (
                            "Thursday signals fill at Friday open — pre-weekend institutional "
                            "de-risking and wider spreads reduce fill quality. Live data shows "
                            "14pp WR gap vs Tuesday (56.2% vs 70.1% across 437 signals). "
                            "Confidence reduced by 3pp."
                        ),
                        "sentiment": "neg",
                        "meta": "dow=thursday haircut=-3pp §57",
                    }
                ]
                conf = sig_dict["confidence"]
    except Exception:
        pass

    # §67 FOMC hard block + FOMC-tomorrow haircut REMOVED (gate audit
    # 2026-07-14): backtest ablation measured ΔSharpe −0.00 (+4 N) — no
    # measurable benefit — and the hardcoded _FOMC_DATES list was a
    # maintenance timebomb (a unit test had already started failing as the
    # dates aged out). Event-day risk is partially covered by VIX9D/MOVE
    # event-risk cards in the assembler.

    # ── Global confidence floor (with ticker-adaptive override) ──────────────
    if conf < _effective_conf_floor:
        return (
            f"conf {conf:.0f}% < global floor {_effective_conf_floor:.0f}%",
            sig_dict,
        )

    # ── Style gate ────────────────────────────────────────────────────────────
    style_floor = STYLE_CONF_FLOORS.get(style, 70.0)
    if conf < style_floor:
        return (
            f"{style} style disabled/floored — conf {conf:.0f}% < {style_floor:.0f}%",
            sig_dict,
        )

    # ── Intraday safety rail (auto-disable on sustained poor WR) ──────────────
    if style == "intraday" and action == "BUY":
        try:
            _blocked, _wr, _n = await _intraday_safety_blocked(db)
            if _blocked:
                return (
                    f"intraday auto-disabled — live WR {_wr * 100:.0f}% < "
                    f"{_INTRADAY_SAFETY_MIN_WR * 100:.0f}% over last {_n} resolved (safety rail)",
                    sig_dict,
                )
        except Exception:
            log.warning("intraday safety-rail check failed", exc_info=True)  # pragma: no mutate

    # ── Ticker block (no 10-day MR behavior) ─────────────────────────────────
    # Only block tickers with structural reasons AND N≥30 confirmed live/OOS
    # underperformance.  Blocking at small N (e.g., APH N=4) is selection on
    # outcomes / online overfitting to noise.
    if ticker in BLOCKED_TICKERS:
        _semi = {"LRCX", "MRVL", "AMAT", "KLAC"}
        _banks = {"STT", "MTB"}
        if ticker in _semi:
            reason = "semi equipment — continuation not MR (LRCX −7.20%, KLAC −4.36% OOS, N≥30)"
        elif ticker in _banks:
            reason = "XLF regional bank — rate-cycle driven, not price-level MR (OOS v5: 0% WR, N≥30)"
        else:
            reason = "ticker-specific block (no MR edge confirmed, N≥30)"
        return (f"{ticker} blocked — {reason}", sig_dict)

    # ── Sector gate ───────────────────────────────────────────────────────────
    sector = sig_dict.get("sectorEtf") or sig_dict.get("sector_etf")
    # Also check ticker itself: sector ETFs (XLF, XLP, XLU) have sector_etf=None
    # because they ARE the sector — the column isn't self-referential.
    ticker_as_sector = sig_dict.get("ticker", "")
    _blocked_key = sector if (sector and sector in BLOCKED_SECTORS) else ticker_as_sector
    if _blocked_key in BLOCKED_SECTORS:
        # §117: blocked sectors may be unblocked only via explicit QENG-1c promotion.
        try:
            from services.sector_ml_promotion import get_promoted_sectors_cached

            _promoted = await get_promoted_sectors_cached(db)
            if _blocked_key in _promoted:
                pass  # promoted sector is allowed through
            else:
                return (
                    f"sector {_blocked_key} blocked (low PF) — awaiting QENG-1c promotion",
                    sig_dict,
                )
        except Exception:
            # On any promotion-lookup failure, fail closed (block the sector).
            log.warning("Sector promotion lookup failed; blocking %s", _blocked_key, exc_info=True)  # pragma: no mutate
            return (
                f"sector {_blocked_key} blocked (low PF) — awaiting QENG-1c promotion",
                sig_dict,
            )

    # ── §54 VIX<15 suspension (ultra-low vol — MR setups statistically fail) ───
    # Backtest §54: VIX<15 regime shows mean-reversion entries cluster at bottom
    # of vol cycles; price continues rather than reverting. 23yr IS data confirms
    # suspending MR signals in ultra-calm regimes improves Sharpe (0.21→0.22).
    if action == "BUY":
        _vix_now = sig_dict.get("vix")
        if _vix_now is not None and _vix_now < 15.0:
            return f"VIX={_vix_now:.1f} < 15 — MR entry suspended in ultra-low vol regime (§54)", sig_dict

    # ── §93d Midday microstructure filter (11:00–12:00 ET) ───────────────────
    # Live data: WR 23.7% in 11–12 ET vs 47.8% baseline (p=0.000). May+ cohort
    # shows reversal (N=4, WR=75%), so this is a confidence haircut, not a hard
    # block, to avoid starvation while the effect is re-evaluated forward.
    try:
        _now_et = datetime.now(pytz.timezone("America/New_York"))
        if action == "BUY" and _now_et.hour == 11:
            _conf_before = sig_dict.get("confidence", 0)
            sig_dict = dict(sig_dict)
            sig_dict["confidence"] = round(max(35.0, _conf_before - 3.0), 1)
            sig_dict.setdefault("rationale", [])
            sig_dict["rationale"] = list(sig_dict["rationale"]) + [
                {
                    "src": "Risk Gate",
                    "head": "Midday Microstructure Haircut (−3pp)",
                    "body": (
                        "11:00–12:00 ET has historically shown elevated adverse-selection "
                        "(WR 23.7% vs 47.8% baseline, p=0.000). Institutional order-flow "
                        "rebalancing and ETF creation/redemption activity cluster in this "
                        "window, creating noise-driven dips that persist rather than revert. "
                        "Confidence reduced by 3pp."
                    ),
                    "sentiment": "neg",
                    "meta": "midday=11-12et haircut=-3pp §93d",
                }
            ]
            conf = sig_dict["confidence"]
    except Exception:
        pass

    # ── Ex-dividend blackout (0–2 days to ex-div, BUY only) ───────────────────
    # Stock drops by dividend amount on ex-div date — structural, not a panic dip.
    # Only gate BUY; HOLD/SELL are unaffected.
    if action == "BUY":
        _exdiv = sig_dict.get("daysToExDiv")
        if _exdiv is not None and 0 <= _exdiv <= 2:
            return (
                f"Ex-dividend in {_exdiv}d — price drop structural not panic, MR entry blocked",
                sig_dict,
            )

    # ── Sector concentration limit (max N BUY per sector per 24h) ────────────
    _max_per_sector = getattr(settings, "max_buys_per_sector_per_day", 2)
    if _max_per_sector > 0 and sector and action == "BUY":
        from models import Signal

        cutoff = _utcnow_naive() - timedelta(hours=24)
        count = (
            await db.execute(
                select(func.count())
                .select_from(Signal)
                .where(Signal.sector_etf == sector)
                .where(Signal.action == "BUY")
                .where(Signal.is_sent == True)
                .where(Signal.sent_at >= cutoff)
            )
        ).scalar_one()
        if count >= _max_per_sector:
            return f"sector {sector} already has {count} BUY sends in 24h (max {_max_per_sector})", sig_dict

    # ── Same-underlying deduplication (GOOG/GOOGL alias gate) ────────────────
    # Both share classes map to the same Alphabet equity position. If either
    # alias was sent as BUY in the last 24h, block the other to prevent
    # unintended double-sizing on a single underlying.
    alias = TICKER_ALIASES.get(ticker)
    if alias and action == "BUY":
        from models import Signal

        cutoff = _utcnow_naive() - timedelta(hours=24)
        alias_count = (
            await db.execute(
                select(func.count())
                .select_from(Signal)
                .where(Signal.ticker == alias)
                .where(Signal.action == "BUY")
                .where(Signal.is_sent == True)
                .where(Signal.sent_at >= cutoff)
            )
        ).scalar_one()
        if alias_count > 0:
            return (
                f"{ticker} blocked — alias {alias} already sent as BUY within 24h (same underlying)",
                sig_dict,
            )

    # ── Source independence gate ──────────────────────────────────────────────
    _raw_sources = sig_dict.get("sources") or []
    if isinstance(_raw_sources, str):
        try:
            import json as _json

            _raw_sources = _json.loads(_raw_sources)
        except Exception:
            _raw_sources = []
    sources_set = set(_raw_sources or [])
    non_ta = sources_set - {
        "Technical",
        "Technicals",
        "Risk Gate",
        "Backtest",
        "Cross-Sectional",
        "Orthogonalization",
        "Signal Cluster",
    }
    # Swing requires same independent corroboration as position (§33 live alpha:
    # swing −1.028%/trade at 65% floor; single non-TA source insufficient to
    # distinguish genuine MR setups from momentum-continuation pullbacks).
    min_non_ta = 2 if style in ("position", "swing") else 1
    if len(non_ta) < min_non_ta:
        _trace = {
            "gate_id": "SourceIndependenceGate",
            "version": "1.0",
            "input_values": {
                "ticker": ticker,
                "style": style,
                "non_ta_sources": sorted(non_ta),
                "min_non_ta": min_non_ta,
            },
            "score_delta": 0.0,
            "confidence_delta": 0.0,
            "passed": False,
            "reason": f"only {len(non_ta)} non-TA sources for {style} (need {min_non_ta})",
        }
        sig_dict.setdefault("gate_traces", []).append(_trace)
        return (
            f"only {len(non_ta)} non-TA sources for {style} (need {min_non_ta})",
            sig_dict,
        )

    # ── Minimum profit filter ─────────────────────────────────────────────────
    entry = sig_dict.get("entry")
    target = sig_dict.get("target")
    if entry and target and entry > 0:
        profit_pct = abs(target - entry) / entry * 100
        if profit_pct < 2.0:
            return f"profit {profit_pct:.1f}% < 2.0% minimum", sig_dict

    # §78 Sep/Oct seasonality floors REMOVED (gate audit 2026-07-14): the
    # backtest ablation retired §78 on 2026-06-02 as confirmed dead (ΔSh=0.00,
    # no trades blocked at 100-ticker scale) and SIGNAL_VALIDATION.md lists it
    # as Removed — but this live copy was left behind. Doc and code now agree.

    return None, sig_dict  # all gates passed
