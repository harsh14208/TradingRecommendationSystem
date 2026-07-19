"""Final-signal assembler (BE-1 refactor).

``_assemble_signal`` extracted verbatim from ``signal_engine.py``. Applies risk
gates, calibrates confidence, derives style, and builds the final signal dict.
"""

import logging
import math
import os
from datetime import datetime, timezone
from typing import Optional

import numpy as _np

from services.engines.helpers import (
    _ET,
    _LEVERAGED_ETFS,
    _SECTOR_MR_CONFIG,
    _current_session,
    _levels,
    _make_plain_english,
    _score_to_action,
)
from services.gates.ticker_performance import TickerPerformanceGate
from services.gates.warning import apply_warning_deconfliction
from services.sector import SECTOR_MAP
from services.sector_ml_promotion import effective_sector_config

log = logging.getLogger("signal.trade.engine")


def _effective_sector_config(sector_etf: str | None, promoted_sectors: set[str] | None) -> dict:
    """Return sector MR config with buy_thresh cleared for promoted blocked sectors."""
    base = _SECTOR_MR_CONFIG.get(sector_etf, {})
    return effective_sector_config(sector_etf, base, promoted_sectors)


def _assemble_signal(
    *,
    ticker: str,
    info: dict,
    tech: dict,
    score: float,
    rationale: list,
    sources: set,
    _force_hold: bool,
    _is_low_atr: bool,
    _atr_pct_pre: float,
    total_confidence_penalty: float,
    portfolio_size_scale: float = 1.0,
    avg_sent: float,
    price: float,
    atr: float,
    market_ctx: Optional[dict],
    earnings_cal: dict,
    sector_rs: Optional[dict],
    days_to_earnings: Optional[int],
    opt_flow: Optional[dict] = None,
    _is_lev_etf: bool = False,
    data_warnings: Optional[list[dict]] = None,
    days_to_exdiv: Optional[int] = None,
    promoted_sectors: Optional[set[str]] = None,
) -> Optional[dict]:
    """
    Apply risk gates, calibrate confidence, derive style, and build
    the final signal dict. Returns None if action is forced to HOLD
    and confidence < threshold.
    """
    # Derive macro/regime variables from market_ctx inline.
    macro = (market_ctx or {}).get("macro") or {}
    vix = macro.get("vix")
    sp500_trend = macro.get("sp500_trend")

    # ── MR entry condition flags — computed early so all downstream gates can use them ─
    # These are referenced by the VIX gate (~line 829) and many later gates;
    # defining them here once prevents UnboundLocalError from forward-references.
    _mr_bb = tech.get("bb_pct_b")
    _mr_ibs = tech.get("ibs")
    _mr_vwap = tech.get("vwap_pct")
    # MR-count: ≥1 of 4 oversold conditions (reverted 2→1 on 2026-06-17).
    # Backtest called 1-vs-2 a wash (MR-count=1 → 155 trades, Sh 0.20;
    # MR-count=2 → 154 trades, Sh 0.21 — +0.01 Sh, −1 trade over 23yr), but in
    # the live trending market the 2-condition requirement collapsed the MR pass
    # rate to ~0.6% (1/170 BUYs over 10 days) → near-zero delivery. Reverted to 1
    # to restore deliverable volume on dip days at a backtest-neutral cost.
    _rsi = tech.get("rsi")
    _mr_rsi_trig = float(_rsi if _rsi is not None else 50) < 42
    _mr_bb_trig = _mr_bb is not None and float(_mr_bb) < 0.22
    _mr_ibs_trig = _mr_ibs is not None and float(_mr_ibs) < 0.15
    _mr_vwap_trig = _mr_vwap is not None and float(_mr_vwap) < -0.75
    _has_mr = sum([_mr_rsi_trig, _mr_bb_trig, _mr_ibs_trig, _mr_vwap_trig]) >= 1

    # SELL MR-setup mirror: ≥1 overbought condition.
    _mr_sell_rsi_trig = _rsi is not None and float(_rsi) > 58
    _mr_sell_bb_trig = _mr_bb is not None and float(_mr_bb) > 0.78
    _mr_sell_ibs_trig = _mr_ibs is not None and float(_mr_ibs) > 0.85
    _mr_sell_vwap_trig = _mr_vwap is not None and float(_mr_vwap) > 0.75
    _has_mr_sell = sum([_mr_sell_rsi_trig, _mr_sell_bb_trig, _mr_sell_ibs_trig, _mr_sell_vwap_trig]) >= 1

    # Telemetry accumulator for assembler-level gates that run before GatePipeline.
    _assembler_traces: list[dict] = []

    def _trace(gate_id: str, passed: bool, reason: str | None, **inputs) -> None:
        _assembler_traces.append(
            {
                "gate_id": gate_id,
                "version": "1.0",
                "input_values": {"ticker": ticker, **inputs},
                "score_delta": 0.0,
                "confidence_delta": 0.0,
                "passed": passed,
                "reason": reason,
            }
        )

    # ── Assemble final signal ───────────────────────────────────────
    # Enforce any blackout/gate that set _force_hold=True mid-scoring.
    # score=0 alone is not sufficient because subsequent signal blocks
    # (e.g. macro, options, institutional) can re-inflate it back above
    # the ±25 BUY/SELL threshold. The flag survives all subsequent scoring.
    if _force_hold:
        score = 0.0  # ensure no stale residual from post-zero signals

    data_warnings = data_warnings or []
    if data_warnings:
        sources.add("Data Quality")
        affected = ", ".join(w.get("source", "unknown") for w in data_warnings[:4])
        extra = "" if len(data_warnings) <= 4 else f" and {len(data_warnings) - 4} more"
        rationale.append(
            {
                "src": "Data Quality",
                "head": "Partial Data Degradation",
                "body": (
                    f"{ticker} signal generated with partial provider coverage. "
                    f"Unavailable source(s): {affected}{extra}. Technical scoring still ran, "
                    "but confidence should be interpreted with this data gap in mind."
                ),
                "sentiment": "neu",
                "meta": "missing_sources=" + ",".join(w.get("source", "unknown") for w in data_warnings),
            }
        )

    # Agreement count excludes meta-signals that are artifacts of the scoring
    # machinery rather than independent evidence (Risk Gate, Orthogonalization,
    # Signal Cluster, Backtest). Counting them inflated the agreement bonus for
    # any signal with many firing post-processing checks.
    _META_SRCS = {"Risk Gate", "Orthogonalization", "Signal Cluster", "Backtest"}
    agree_sent = "pos" if score > 0 else "neg"
    agreement = sum(1 for r in rationale if r.get("sentiment") == agree_sent and r.get("src") not in _META_SRCS)
    action, confidence = _score_to_action(score, agreement)

    # ── VIX9D — Near-Term Event Risk ─────────────────────────────────────
    _vix9d_ratio = macro.get("vix9d_ratio")
    if _vix9d_ratio is not None and _vix9d_ratio > 1.10 and action in ("BUY", "SELL"):
        _vix9d = macro.get("vix9d", 0)
        confidence = round(max(35.0, confidence - 4), 1)
        sources.add("Macro")
        rationale.append(
            {
                "src": "Macro",
                "head": f"Near-Term Event Risk (VIX9D/VIX {_vix9d_ratio:.2f}×) — Confidence −4pp",
                "body": (
                    f"9-day VIX ({_vix9d:.1f}) is {_vix9d_ratio:.2f}× the spot VIX. "
                    "Near-term options demand is concentrated — a known upcoming event (earnings, "
                    "FOMC, CPI) is distorting short-horizon signals. Wait for post-event clarity "
                    "before acting on this signal."
                ),
                "sentiment": "neg",
                "meta": f"VIX9D/VIX = {_vix9d_ratio:.2f}×",
            }
        )

    # ── MOVE Index — Bond Market Stress ──────────────────────────────────
    _move = macro.get("move")
    if _move is not None and _move > 140 and action == "BUY":
        confidence = round(max(35.0, confidence - 5), 1)
        sources.add("Macro")
        rationale.append(
            {
                "src": "Macro",
                "head": f"Treasury Vol Stress (MOVE {_move:.0f}) — Confidence −5pp",
                "body": (
                    f"CBOE MOVE Index at {_move:.0f} — bond market implied vol is highly elevated. "
                    "Elevated MOVE historically leads equity drawdowns by 2–3 weeks. "
                    "Reduce position sizing until MOVE normalises below 120."
                ),
                "sentiment": "neg",
                "meta": f"^MOVE = {_move:.0f}",
            }
        )

    # ── STLFSI4 — Financial Stress (macro signal into single-stock) ───────
    _stlfsi = macro.get("stlfsi")
    if _stlfsi is not None and _stlfsi > 1.0 and action == "BUY":
        confidence = round(min(confidence, 58.0), 1)
        sources.add("Macro")
        rationale.append(
            {
                "src": "Macro",
                "head": f"Financial Stress Override (STLFSI4 {_stlfsi:+.2f}) — BUY Cap 58%",
                "body": (
                    f"St. Louis Financial Stress Index at {_stlfsi:+.2f} (>1.0 = crisis). "
                    "In high-stress regimes, even strong individual-stock setups frequently fail "
                    "because correlated forced selling overrides fundamentals. BUY confidence "
                    "capped at 58% until FSI returns below 0.5."
                ),
                "sentiment": "neg",
                "meta": f"STLFSI4 = {_stlfsi:+.3f}",
            }
        )

    # Enforce blackout action regardless of what _score_to_action computed.
    if _force_hold:
        action = "HOLD"

    # ── Chronic-Loser Ticker Exclusion ──────────────────────────────────
    adaptive = (market_ctx or {}).get("adaptive_weights", {})
    ticker_wrs = adaptive.get("ticker_win_rates", {})
    ticker_wr = ticker_wrs.get(ticker)
    if action == "BUY" and ticker_wr is not None and ticker_wr < 0.45:
        action = "HOLD"
        _trace(
            "ChronicLoserExclusionGate",
            False,
            f"{ticker} historical win rate {ticker_wr * 100:.0f}% < 45%",
            ticker_win_rate=round(ticker_wr, 3),
        )
        sources.add("Risk Gate")
        rationale.append(
            {
                "src": "Risk Gate",
                "head": f"Chronic Loser Exclusion — Win Rate {ticker_wr * 100:.0f}%",
                "body": (
                    f"{ticker} has a historical win rate below 45%. BUY signals on "
                    "persistent structural underperformers are mathematically "
                    "negative expected value. Signal excluded."
                ),
                "sentiment": "neg",
                "meta": f"Win rate {ticker_wr * 100:.0f}% < 45%",
            }
        )

    # ── True Orthogonality Minimum ──────────────────────────────────────
    _core_families = {
        "Technical",
        "Options",
        "13F",
        "SEC EDGAR",
        "Congress",
        "Fundamentals",
        "Macro",
        "Dark Pool",
        "Short Interest",
        "Analyst",
        "Social",
    }
    _active_families = len([s for s in sources if s in _core_families])
    if action == "BUY" and _active_families < 3 and score < 50:
        action = "HOLD"
        _trace(
            "TrueOrthogonalityMinimumGate",
            False,
            f"Only {_active_families}/3 independent source families (score {score:.1f} < 50)",
            active_families=_active_families,
            score=score,
        )
        sources.add("Risk Gate")
        rationale.append(
            {
                "src": "Risk Gate",
                "head": f"Orthogonality Gate — Only {_active_families}/3 Source Families",
                "body": (
                    "A reliable BUY signal requires convergence from at least 3 independent "
                    "data families (e.g., Technical + Options + Fundamentals). Correlated "
                    "indicators within the same family do not provide enough independent edge."
                ),
                "sentiment": "neg",
                "meta": f"Active families: {_active_families} < 3",
            }
        )

    # ── Technical-Only SELL Gate ────────────────────────────────────────
    # 30-year backtest shows technical-only SELL signals average -0.71%/trade.
    # Require at least one non-technical confirmation (Options, Macro, News, etc.)
    _alt_data_sources = {
        "Options",
        "Macro",
        "13F",
        "SEC EDGAR",
        "Dark Pool",
        "Insider",
        "Congress",
        "Analyst",
        "Fundamentals",
        "Earnings",
        "Benzinga",
        "Finnhub",
        "Reuters",
        "Finviz",
        "Social",
    }
    _has_alt = any(s in _alt_data_sources for s in sources)
    if action == "SELL" and not _has_alt:
        action = "HOLD"
        _trace(
            "TechnicalOnlySellGate",
            False,
            "SELL missing alternative-data confirmation",
            sources=sorted(sources),
        )
        sources.add("Risk Gate")
        rationale.append(
            {
                "src": "Risk Gate",
                "head": "Technical-Only SELL Gate — Missing Alt-Data Confirmation",
                "body": (
                    "30-year backtesting shows technical-only SELL signals have negative "
                    "expected value (-0.71% avg return). SELL signals require confirmation "
                    "from at least one alternative data source (Options, Macro, News, etc.) "
                    "to fire. Signal gated to HOLD."
                ),
                "sentiment": "neg",
                "meta": "technical_only_sell=True",
            }
        )

    # ── Volume / liquidity / momentum-quality pipeline ──────────────────────
    # Constructs a SignalContext once (reused by all downstream pipelines).
    # rationale and sources are the same list/set objects — mutated in place.
    from services.gates.base import GatePipeline, SignalContext as _SCtx
    from services.gates.volume import (
        AdxGate,
        DollarVolumeGate,
        OverboughtWeakTrendGate,
        RvolGate,
    )

    _se_sector_etf_ctx = (sector_rs or {}).get("sector_etf") or SECTOR_MAP.get(ticker.upper(), "")
    _sig_ctx = _SCtx(
        action=action,
        confidence=confidence,
        score=score,
        rationale=rationale,
        sources=sources,
        ticker=ticker,
        tech=tech,
        info=info,
        macro=macro,
        price=price,
        atr=atr,
        has_mr=_has_mr,
        vix=vix,
        sp500_trend=sp500_trend,
        sector_etf=_se_sector_etf_ctx,
        today_dow=datetime.now(_ET).weekday(),
        month=datetime.now(timezone.utc).month,
        opt_flow=opt_flow,
        sector_rs=sector_rs,
        earnings_cal=earnings_cal,
        days_to_earnings=days_to_earnings,
        is_low_atr=_is_low_atr,
        atr_pct_pre=_atr_pct_pre,
        sector_config=_effective_sector_config(_se_sector_etf_ctx, promoted_sectors),
        is_lev_etf=_is_lev_etf,
    )

    # Attach assembler-level traces so they persist with the technical gate traces.
    _sig_ctx.gate_traces.extend(_assembler_traces)

    GatePipeline([RvolGate(), AdxGate(), OverboughtWeakTrendGate(), DollarVolumeGate()]).run(_sig_ctx)

    # Sync mutable state back; rationale/sources already mutated in place.
    action = _sig_ctx.action
    confidence = _sig_ctx.confidence
    score = _sig_ctx.score
    # Keep aliases needed by remaining inline gates below.
    _adx_gate = tech.get("adx")
    _rsi_gate = float(tech.get("rsi") or 50)

    # Low-volatility (min-ATR 0.7%) BUY gate REMOVED (gate audit 2026-07-14):
    # 1 fire in 87,982 all-time signals — the floor never binds on the current
    # universe. Its claimed "20-year backtest" has no entry in the validation
    # ledger, and low-ATR defensives are covered by the cohort-EV gate +
    # ticker_performance gate from live data.

    # ── Defensive-ticker BUY gate ────────────────────────────────────────
    # Tickers that showed 0% BUY win rate across ≥3 resolved signals in the
    # May 2026 validation (n=529). These span low-vol defensives, banks, and
    # consumer staples where momentum signals structurally misfire.
    # The ATR gate above catches KO/PEP/T; this gate covers higher-ATR names
    # (BAC, C, USB, PNC, TGT, etc.) that slip past the ATR threshold.
    _DEFENSIVE_BUY_BLOCK = {
        # Live-validated 0% BUY win rate (May 2026, n=529 resolved signals).
        # All entries here come from FORWARD performance data — NOT from
        # the 20yr backtest. Backtest-derived exclusions were removed (audit
        # finding: hardcoding tickers found via historical backtest is look-ahead
        # selection bias). The dynamic AR(1) momentum-persistence gate below
        # replaces those exclusions with a point-in-time quantitative rule.
        "KO",
        "PEP",
        "T",
        "NEE",
        "PG",
        "USB",
        "PNC",
        "C",
        "AIG",
        "WM",
        "MCO",
        "TT",
        "DE",
        "TJX",
        # Live validated 0% WR (May 2026, §11b ticker analysis)
        "APH",  # 0/4 trades, avg -8.70% — worst live ticker
        "EOG",  # 0/2 trades, avg -7.00% — energy, structurally weak on MR signals
        "SYK",  # 0/1 trades, avg -6.81% — healthcare, earnings-driven not technical
        "CVX",  # 0/2 trades, avg -5.99% — energy/macro driven
        "UPS",  # 0/1 trades, avg -6.31% — logistics, cyclical/macro not chart
        # Backtest-validated: event-driven / range-bound / non-technical
        # Pharma (drug-approval dominated, not chart-driven)
        "ABBV",
        "MRK",
        "PFE",
        "LLY",
        "TMO",
        # Consumer staples / tobacco (low-ATR, mean-reverting)
        "PM",
        "WMT",
        # Analog/commodity semiconductors (earnings-cycle driven)
        "TXN",
        # Consumer brand (fashion cycles, not technical)
        "NKE",
        # Payments (behaves like a financial in stress)
        "V",
        # TSLA, SBUX, GS, MA, BLK, SCHW, PANW, GEN, CPAY — REMOVED.
        # Were added based on 20yr backtest negative avg return (look-ahead bias).
        # Now handled dynamically by the AR(1) momentum-persistence gate below.
    }
    _static_blocked = action == "BUY" and ticker in _DEFENSIVE_BUY_BLOCK
    if _static_blocked:
        action = "HOLD"
        _trace(
            "DefensiveTickerBuyGate",
            False,
            f"{ticker} is in the defensive BUY block list",
            blocked_reason="live 0% WR or backtest-negative expected value",
        )
        sources.add("Risk Gate")
        rationale.append(
            {
                "src": "Risk Gate",
                "head": f"Defensive-Ticker BUY Gate — {ticker} Blocked",
                "body": (
                    f"{ticker} is in the defensive block: either 0% live BUY win rate (n≥3) "
                    "or negative avg return across 20yr technical backtest. "
                    "Price action is event-driven, macro-driven, or non-MR-responsive. "
                    "BUY gated to HOLD until re-validation shows positive expected value."
                ),
                "sentiment": "neg",
                "meta": f"Ticker: {ticker} | Gate: defensive_ticker_block",
            }
        )

    # ── Stage B: TickerPerformanceGate (shadow mode) ───────────────────────
    # Point-in-time replacement for the static blocklist above.  It evaluates
    # each ticker's decay-weighted forward win rate over the last 180 days and
    # blocks (or size-reduces) only when there is sufficient negative evidence.
    # In Stage B it runs in shadow mode: it appends a rationale card but never
    # changes the action.  It is controlled by TICKER_PERF_GATE_ENABLED; once
    # 30 days of shadow logs show parity or improvement, the static list above
    # will be removed and this gate will become the hard block.
    _ticker_perf_enabled = os.getenv("TICKER_PERF_GATE_ENABLED", "").lower() in {"1", "true", "yes"}
    _ticker_gate = TickerPerformanceGate(enabled=_ticker_perf_enabled)
    _ticker_gate.apply(_sig_ctx)
    _ticker_decision = _ticker_gate._decide(_sig_ctx)
    if _ticker_perf_enabled:
        action = _sig_ctx.action

    # Structured shadow-decision payload for the 30-day static-vs-dynamic A/B.
    # This is persisted by scanner.py into ticker_perf_shadow_decisions.
    _ticker_perf_shadow: dict | None = None
    if action in ("BUY", "SELL") or _static_blocked or _ticker_decision.block or _ticker_decision.size_mult < 1.0:
        _ticker_perf_shadow = {
            "ticker": ticker,
            "action": "BUY" if _static_blocked or _sig_ctx.action == "BUY" else action,
            "sector_etf": _se_sector_etf_ctx,
            "static_blocked": _static_blocked,
            "dynamic_decision": "block"
            if _ticker_decision.block
            else ("caution" if _ticker_decision.size_mult < 1.0 else "pass"),
            "dynamic_reason": _ticker_decision.reason,
            "dynamic_n": _ticker_decision.n,
            "dynamic_decay_wr": _ticker_decision.win_rate,
            "dynamic_raw_wr": _ticker_decision.raw_wr,
            "dynamic_size_mult": _ticker_decision.size_mult,
            "hold_days": None,  # filled later by scanner.py once style is finalized
        }
    if _static_blocked and not _ticker_decision.block:
        log.info(
            "[ticker_perf_shadow] %s: static blocklist blocked, ticker gate would NOT block (%s)",
            ticker,
            _ticker_decision.reason,
        )
    elif not _static_blocked and _ticker_decision.block:
        log.info(
            "[ticker_perf_shadow] %s: static blocklist passed, ticker gate WOULD block (%s)",
            ticker,
            _ticker_decision.reason,
        )

    # ── Fundamental Value-Trap Gate (see gates/fundamentals.py) ─────────────
    from services.gates.fundamentals import FundamentalValueTrapGate as _VTGate

    _sig_ctx.action = action
    _sig_ctx.confidence = confidence
    _sig_ctx.score = score
    GatePipeline([_VTGate()]).run(_sig_ctx)
    action = _sig_ctx.action
    confidence = _sig_ctx.confidence
    score = _sig_ctx.score

    # ── Leveraged / inverse-leveraged ETF disclosure ─────────────────────
    # Always fire for any leveraged ETF signal, regardless of action.
    # Fundamentals, earnings, and insider scoring are already bypassed upstream;
    # this card surfaces the decay risk to the user and confirms the bypass.
    if ticker in _LEVERAGED_ETFS:
        _lev_bull = ticker not in {
            "SQQQ",
            "SPXS",
            "SPXU",
            "SOXS",
            "TECS",
            "FAZ",
            "TZA",
            "LABD",
            "FNGD",
            "YANG",
            "DRV",
            "TMV",
            "HIBS",
            "SRTY",
            "DRIP",
            "DUST",
            "JDST",
            "SCO",
            "SDS",
            "QID",
            "REW",
            "TWM",
        }
        _mult = (
            "3×"
            if ticker
            not in {
                "GUSH",
                "DRIP",
                "NUGT",
                "DUST",
                "JNUG",
                "JDST",
                "UCO",
                "SCO",
                "SSO",
                "SDS",
                "QLD",
                "QID",
                "ROM",
                "REW",
                "UWM",
                "TWM",
                "INDL",
            }
            else "2×"
        )
        _dir = "Bull" if _lev_bull else "Bear (Inverse)"
        sources.add("Risk Gate")
        rationale.append(
            {
                "src": "Risk Gate",
                "head": f"{_mult} Leveraged ETF — {_dir} | Hold ≤5 Days",
                "body": (
                    f"{ticker} is a {_mult} {_dir} leveraged ETF. Each 1% move in the "
                    f"underlying index produces approximately {_mult} in this ETF. "
                    "Key risks: (1) Volatility decay — daily rebalancing causes "
                    "compounding drag; a 10% round-trip in the underlying can cost "
                    "2–8% of NAV even if price returns to start. "
                    "(2) No fundamental scoring — P/E, FCF, earnings, insider activity, "
                    "and analyst revisions are not applicable and have been bypassed. "
                    "(3) Signals are based on technical and macro factors only. "
                    "Recommended maximum hold: swing (2–5 trading days). "
                    "Use position sizing of ⅓ or less vs an equivalent single-stock trade."
                ),
                "sentiment": "neg",
                "meta": f"type=leveraged_etf | mult={_mult} | dir={'bull' if _lev_bull else 'bear'}",
            }
        )

    # ── Market-cap tier modifier ──────────────────────────────────────────
    # Mega-caps ($500B+) have wall-to-wall analyst coverage, crowded positioning,
    # and slower momentum decay — momentum signals are less differentiated.
    # Small-caps (<$2B) add a volatility premium notice to the rationale.
    _mktcap = info.get("market_cap")
    if _mktcap and action in ("BUY", "SELL") and not _is_lev_etf:
        if _mktcap >= 500_000_000_000:  # mega-cap ≥ $500B
            confidence = round(max(35.0, confidence - 2), 1)
            sources.add("Risk Gate")
            rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Mega-Cap Crowding Haircut (${_mktcap / 1e12:.1f}T)",
                    "body": (
                        f"Market cap of ${_mktcap / 1e12:.1f}T means this stock has wall-to-wall analyst "
                        "coverage, crowded institutional positioning, and slower-decaying momentum. "
                        "Edge is smaller vs mid/small cap — confidence haircut applied."
                    ),
                    "sentiment": "neg",
                    "meta": f"mktcap=${_mktcap / 1e9:.0f}B | tier=mega | adj=-2pp",
                }
            )
        elif _mktcap < 2_000_000_000:  # small-cap < $2B
            sources.add("Risk Gate")
            rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Small-Cap Volatility Notice (${_mktcap / 1e9:.1f}B)",
                    "body": (
                        f"Market cap of ${_mktcap / 1e9:.1f}B — small-cap territory. Higher volatility, "
                        "wider bid-ask spreads, and lower liquidity amplify both gains and losses. "
                        "Size position accordingly (suggest ½ of normal allocation)."
                    ),
                    "sentiment": "neg",
                    "meta": f"mktcap=${_mktcap / 1e9:.1f}B | tier=small",
                }
            )

    # ── Pre-options technicals pipeline (Part 1: stress + regime + SMA gates) ─────
    # Runs: StlfsiVixGate → GlobalVixMinGate → Sma200BuyGate → SellUptrendGate
    #       → SpyNeutralZoneGate → MacroSma200Gate → BearHighVixGate
    from services.gates.technicals import (
        BearHighVixGate as _BHVGate,
        GlobalVixMinGate as _GVMGate,
        MacroSma200Gate as _MacroS200Gate,
        Sma200BuyGate as _S200Gate,
        SellUptrendGate as _SellUTGate,
        SpyNeutralZoneGate as _SpyNZGate,
        StlfsiVixGate as _StlfsiGate,
    )

    _sig_ctx.action = action
    _sig_ctx.confidence = confidence
    _sig_ctx.score = score
    GatePipeline(
        [
            _StlfsiGate(),
            _GVMGate(),
            _S200Gate(),
            _SellUTGate(),
            _SpyNZGate(),
            _MacroS200Gate(),
            _BHVGate(),
        ]
    ).run(_sig_ctx)
    action = _sig_ctx.action
    confidence = _sig_ctx.confidence
    score = _sig_ctx.score

    # ── BUY:SELL saturation circuit breaker ─────────────────────────────
    # When the rolling 7-day BUY:SELL ratio exceeds 4:1, the system is over-
    # optimistic. Raise the effective BUY threshold to 42 so only high-conviction
    # signals survive. SELL signals are never suppressed by this gate — the
    # circuit breaker only corrects the bullish bias, not the bearish direction.
    if action == "BUY" and (market_ctx or {}).get("buy_saturated") and score < 42:
        action = "HOLD"
        _ratio = (market_ctx or {}).get("buy_sell_ratio", 4.0)
        _trace(
            "BuySaturationGate",
            False,
            f"7d BUY:SELL ratio {_ratio:.1f}:1 with score {score:.1f} < 42",
            buy_sell_ratio=_ratio,
            score=score,
        )
        sources.add("Risk Gate")
        rationale.append(
            {
                "src": "Risk Gate",
                "head": f"BUY Saturation Gate — 7d BUY:SELL Ratio {_ratio:.1f}:1 (>4.0)",
                "body": (
                    f"The system has generated {_ratio:.1f} BUY signals for every SELL signal "
                    "over the past 7 days — a sign of structural over-optimism. "
                    "Marginal BUY signals (score <42) are suppressed until the ratio normalises below 4.0."
                ),
                "sentiment": "neg",
                "meta": f"7d BUY:SELL = {_ratio:.1f}:1 | Score: {score:.1f}",
            }
        )

    # ── Broad market breadth BUY gate ───────────────────────────────────
    # When >70% of S&P 500 stocks are above their 200-DMA, the technical
    # baseline is already elevated: Supertrend, price structure, and momentum
    # signals all default positive, adding ~+15 pts before any real edge fires.
    # Require a stronger score (≥42) to confirm genuine alpha beyond the tide.
    # SELL signals are never gated here — breadth strength doesn't protect shorts.
    if action == "BUY" and score < 42:
        _breadth_ctx = (market_ctx or {}).get("breadth") or {}
        _pct_200 = _breadth_ctx.get("pct_above_200d", 0) or 0
        if _pct_200 > 70:
            action = "HOLD"
            _trace(
                "BroadMarketBreadthGate",
                False,
                f"{_pct_200:.0f}% of S&P 500 above 200-DMA and score {score:.0f} < 42",
                pct_above_200d=_pct_200,
                score=score,
            )
            sources.add("Risk Gate")
            rationale.append(
                {
                    "src": "Risk Gate",
                    "head": f"Broad Market Breadth Gate — {_pct_200:.0f}% Above 200-DMA (Score {score:.0f} < 42)",
                    "body": (
                        f"{_pct_200:.0f}% of S&P 500 stocks are above their 200-day average — "
                        "technical baselines (Supertrend, momentum, price structure) are uniformly "
                        "elevated, adding ~15 pts of structural noise to every BUY signal. "
                        "Requiring score ≥42 ensures only genuine alpha clears the bar."
                    ),
                    "sentiment": "neg",
                    "meta": f"Breadth: {_pct_200:.0f}% >200d | Score: {score:.1f}",
                }
            )

    # ── Pre-options technicals pipeline (Part 2: MR quality gates) ─────────────
    # Runs: MrPersistenceGate → MrEntryConditionGate → IbsSma20ConfluenceGate
    #       → AtrRankFloorGate → SectorVixFloorGate → AtrRankCeilingGate
    #       → ReturnJumpGate → VixDirectionGate
    from services.gates.technicals import (
        AtrRankCeilingGate as _ARCGate,
        AtrRankFloorGate as _ARFGate,
        IbsSma20ConfluenceGate as _IBSGate,
        Max21Gate as _Max21Gate,
        MrEntryConditionGate as _MRECGate,
        MrPersistenceGate as _MRPGate,
        ReturnJumpGate as _RJGate,
        SectorVixFloorGate as _SVFGate,
        VixDirectionGate as _VDGate,
    )

    _sig_ctx.action = action
    _sig_ctx.confidence = confidence
    _sig_ctx.score = score
    GatePipeline(
        [
            _MRPGate(),
            _MRECGate(),
            _IBSGate(),
            _ARFGate(),
            _SVFGate(),
            _ARCGate(),
            _RJGate(),
            _VDGate(),
            _Max21Gate(),
        ]
    ).run(_sig_ctx)
    action = _sig_ctx.action
    confidence = _sig_ctx.confidence
    score = _sig_ctx.score

    # ── Options flow pipeline ───────────────────────────────────────────────
    # _sig_ctx is the same SignalContext object built in the volume pipeline
    # above — reuse it with updated action/confidence/score already synced.
    # Runs: OptionsFlowConfirmationGate → IvRankFlagGate → PutSweepCapitulationGate
    # (IvrMrGate/PutCallSkewGate/IvTermStructureGate removed 2026-07-14 — 0 fires ever)
    from services.gates.options import (
        IvRankFlagGate,
        OptionsFlowConfirmationGate,
        PutSweepCapitulationGate,
    )

    # Refresh mutable state on the context before running (downstream inline
    # gates may have changed action/confidence since the volume pipeline ran).
    _sig_ctx.action = action
    _sig_ctx.confidence = confidence
    _sig_ctx.score = score

    GatePipeline(
        [
            OptionsFlowConfirmationGate(),
            IvRankFlagGate(),
            PutSweepCapitulationGate(),
        ]
    ).run(_sig_ctx)

    action = _sig_ctx.action
    confidence = _sig_ctx.confidence
    score = _sig_ctx.score

    # ── Post-options technicals pipeline ──────────────────────────────────────
    # Runs: SectorScoreFloorGate → NearEarningsCautionGate → DeepBearRsiGate
    #       → SustainedBearGate → PriceSma20DistanceGate
    from services.gates.technicals import (
        DeepBearRsiGate as _DBRGate,
        NearEarningsCautionGate as _NECGate,
        PriceSma20DistanceGate as _PS20Gate,
        SectorScoreFloorGate as _SSFGate,
        SustainedBearGate as _SBGate,
    )

    _sig_ctx.action = action
    _sig_ctx.confidence = confidence
    _sig_ctx.score = score
    GatePipeline(
        [
            _SSFGate(),
            _NECGate(),
            _DBRGate(),
            _SBGate(),
            _PS20Gate(),
        ]
    ).run(_sig_ctx)
    action = _sig_ctx.action
    confidence = _sig_ctx.confidence
    score = _sig_ctx.score

    # ── RS-laggard hard gate (gate-audit 2026-07-15) ─────────────────────────
    # The "Underperforming S&P 500" −12 score penalty fires on 20% of the
    # delivered book (N=85) and that cohort resolves at WR 35.3% (−14.5pp vs
    # baseline) — correctly signed but far too weak, the §77 pattern again.
    # 1M return more than 8pp below SPY = institutional distribution, not a
    # recoverable dip. BUY → HOLD.
    _rs_1m = tech.get("rel_strength_1m")
    if action == "BUY" and _rs_1m is not None and _rs_1m < -8.0:
        action = "HOLD"
        sources.add("Risk Gate")
        rationale.append(
            {
                "src": "Risk Gate",
                "head": f"RS Laggard — {abs(_rs_1m):.1f}% Below S&P (1M), BUY Blocked",
                "body": (
                    f"1-month return trails the S&P 500 by {abs(_rs_1m):.1f}pp. Live audit "
                    "(corrected book, 2026-07-15): delivered BUYs in this cohort won only "
                    "35.3% (−14.5pp vs baseline, N=85) — persistent relative weakness marks "
                    "institutional selling, not a mean-reverting dip. The prior −12 score "
                    "penalty still let these through; BUY is now blocked."
                ),
                "sentiment": "neg",
                "meta": f"rel_strength_1m={_rs_1m:+.1f}pp hard_block (gate-audit 2026-07-15)",
            }
        )

    # ── §57 DOW gate + §77 tax-loss window ─────────────────────────────────
    from services.gates.calendar import apply_calendar_gates as _cal_gates

    _now_et = datetime.now(_ET)
    _today_dow = _now_et.weekday()  # 0=Mon … 4=Fri
    _month_now = _now_et.month
    action, confidence, _cal_cards, _cal_sources = _cal_gates(
        action=action,
        confidence=confidence,
        score=score,
        today_dow=_today_dow,
        month=_month_now,
        price=price,
        info=info,
    )
    rationale.extend(_cal_cards)
    sources.update(_cal_sources)

    # Apply combined post-processing confidence penalty (warning signals + low volume)
    if total_confidence_penalty > 0 and action in ("BUY", "SELL"):
        confidence = round(max(35.0, confidence * (1 - total_confidence_penalty)), 1)

    # ── Macro Contradiction Cap ──────────────────────────────────────────
    # A BUY signal at ≥70% confidence while macro is meaningfully bearish
    # (macro_score < −3) is a contradiction: the stock-level technicals say
    # buy, but the macro environment says sell everything. Cap confidence at
    # 65% to reflect the elevated failure rate of these cross-current setups.
    # Symmetric: a SELL at ≥70% confidence with a bullish macro is capped too.
    #
    # _conf_macro_cap tracks the strictest macro cap so the hard final ceiling
    # can re-enforce it after adaptive win-rate / yield-dampener adjustments,
    # which run later and could otherwise push confidence back above the cap.
    _conf_macro_cap = 72.0  # default = hard ceiling (no active cap)
    if action in ("BUY", "SELL") and confidence >= 70:
        _m_score = macro.get("macro_score", 0) if macro else 0
        _m_contradiction = (_m_score < -3 and action == "BUY") or (_m_score > 3 and action == "SELL")
        if _m_contradiction:
            _conf_macro_cap = min(_conf_macro_cap, 65.0)
            confidence = round(min(confidence, 65.0), 1)
            rationale.append(
                {
                    "src": "Macro",
                    "head": "Macro Contradiction — Confidence Capped at 65%",
                    "body": (
                        f"Macro score is {_m_score:+.0f} ({'bearish' if _m_score < 0 else 'bullish'}), "
                        f"contradicting the {action} signal. High-confidence {action} signals "
                        "in a contradictory macro environment have significantly lower win rates. "
                        "Confidence capped at 65% until macro aligns."
                    ),
                    "sentiment": "neg",
                    "meta": f"Macro score: {_m_score:+.0f} | Action: {action}",
                }
            )

    # ── Macro News Sentiment BUY Cap ─────────────────────────────────────
    # When SPY/QQQ ETF news is strongly negative AND VIX > 20, cap all BUY signals at 65%.
    if action == "BUY":
        _news_sent = (macro or {}).get("macro_news_sentiment")
        _vix_now = (macro or {}).get("vix") or 0
        if _news_sent is not None and _news_sent < -0.3 and _vix_now > 20:
            _new_cap = 65.0
            _conf_macro_cap = min(_conf_macro_cap, _new_cap)
            if confidence > _new_cap:
                confidence = round(min(confidence, _new_cap), 1)
                rationale.append(
                    {
                        "src": "Macro",
                        "head": f"Macro News Negative (SPY/QQQ) — BUY Cap {_new_cap:.0f}%",
                        "body": (
                            f"ETF-level news sentiment is {_news_sent:+.2f} (negative) with VIX at {_vix_now:.1f}. "
                            "Broad-market news fear combined with elevated volatility caps BUY confidence "
                            "until macro news normalises."
                        ),
                        "sentiment": "neg",
                        "meta": f"macro_news_sentiment={_news_sent:+.2f} vix={_vix_now:.1f}",
                    }
                )

    # ── Adaptive confidence from historical win rates (VIX-adjusted) ───────
    # In high-volatility regimes, historical win rates are less predictive —
    # patterns break down when VIX is elevated. Dampen the adjustment accordingly.
    adaptive = (market_ctx or {}).get("adaptive_weights", {})
    if adaptive and action in ("BUY", "SELL"):
        wr_key = f"{action}_win_rate"
        win_rate = adaptive.get(wr_key)
        if win_rate is not None:
            # Volatility dampener: reduce the historical-accuracy adjustment under stress.
            # Thresholds mirror the VIX score multipliers (35/25/15) so both adjustments
            # activate at the same regime boundaries rather than misaligned breakpoints.
            vix_dampener = 1.0
            if vix is not None:
                if vix > 35:
                    vix_dampener = 0.40  # panic regime — history unreliable (mirrors 0.60× score mult)
                elif vix > 25:
                    vix_dampener = 0.60  # elevated vol (mirrors 0.82× score mult)
                elif vix > 15:
                    vix_dampener = 0.85  # slightly elevated (mirrors 1.06× score boost boundary)
            wr_delta = round((win_rate - 0.50) * 16 * vix_dampener, 1)
            confidence = round(min(72.0, max(35.0, confidence + wr_delta)), 1)
            if abs(wr_delta) >= 3:
                sources.add("Backtest")
                direction_lbl = "boosted" if wr_delta > 0 else "reduced"
                vix_note = (
                    f" (VIX {vix:.0f} → {vix_dampener:.0%} dampener applied)"
                    if vix is not None and vix_dampener < 1.0
                    else ""
                )
                rationale.append(
                    {
                        "src": "Backtest",
                        "head": f"Historical {action} Win Rate {win_rate * 100:.0f}% — Confidence {direction_lbl}",
                        "body": (
                            f"Past {action} signals have a {win_rate * 100:.0f}% win rate. "
                            f"Confidence adjusted {'+' if wr_delta > 0 else ''}{wr_delta:.1f} points.{vix_note}"
                        ),
                        "sentiment": "pos" if wr_delta > 0 else "neg",
                        "meta": f"{action} win rate: {win_rate * 100:.0f}%",
                    }
                )

    # ── Consecutive Loss Streak Suppression ─────────────────────────────
    # If this ticker has lost on N consecutive recent resolved signals, penalise
    # confidence by 5pp per loss beyond the first — max −20pp. Prevents the engine
    # from repeatedly issuing high-confidence signals on persistently failing setups.
    if action in ("BUY", "SELL") and adaptive:
        _loss_streaks = adaptive.get("ticker_loss_streaks", {})
        _streak = _loss_streaks.get(ticker, 0)
        if _streak >= 2:
            _streak_penalty = round(min(20.0, (_streak - 1) * 5.0), 1)
            confidence = round(max(35.0, confidence - _streak_penalty), 1)
            sources.add("Backtest")
            rationale.append(
                {
                    "src": "Backtest",
                    "head": f"{_streak}-Signal Loss Streak — Confidence Reduced",
                    "body": (
                        f"{ticker} has lost on {_streak} consecutive resolved signals. "
                        f"Confidence reduced by {_streak_penalty:.0f}pp until a winning signal breaks the streak."
                    ),
                    "sentiment": "neg",
                    "meta": f"Loss streak: {_streak} | Penalty: -{_streak_penalty:.0f}pp",
                }
            )

    # ── VIX Hard Confidence Floor ────────────────────────────────────────
    # Panic regimes (VIX > 30) mechanically increase realized volatility and
    # the correlation of all risk assets — directional edge deteriorates sharply.
    # Signals below 75% confidence have statistically poor win rates in these
    # conditions: "catching falling knives." Hard-gate to HOLD.
    # Confidence is capped at 72 downstream, so a 75 threshold would make this
    # an unconditional block. Use 70 to align with the actual output range.
    if vix is not None and vix > 30 and action in ("BUY", "SELL") and confidence < 70:
        action = "HOLD"
        sources.add("Risk Gate")
        rationale.append(
            {
                "src": "Risk Gate",
                "head": f"VIX Regime Floor — {confidence:.0f}% Below 70% Threshold (VIX {vix:.0f})",
                "body": (
                    f"VIX at {vix:.0f} signals an active panic regime (threshold: 30). "
                    "In elevated-VIX environments, {}-confidence signals have historically poor "
                    "win rates — technical patterns break down as correlations spike and "
                    "liquidity thin outs. Signal gated to HOLD until VIX normalises below 30."
                ).format(f"{confidence:.0f}%"),
                "sentiment": "neg",
                "meta": f"VIX = {vix:.0f} | Min confidence gate: 70% | Actual: {confidence:.0f}%",
            }
        )

    # ── Style derivation from rationale composition ───────────────────────
    # Intraday wins over all — a fresh RSI extreme or Bollinger touch is a
    # short-term reversal play regardless of structural context.
    # Position only fires when genuinely structural signals (strong fundamentals,
    # confirmed institutional buying) dominate with NO short-term overrides.
    # Everything else defaults to swing.
    _heads_str = " || ".join(r.get("head", "") for r in rationale)

    _is_intraday = any(
        kw in _heads_str
        for kw in [
            "RSI Oversold",
            "RSI Overbought",
            "RSI Weakening",
            "RSI Elevated",
            "Bollinger Band Touch",
            "Bullish RSI Divergence",
            "Bearish RSI Divergence",
            "Stochastic Bullish Cross",
            "Stochastic Bearish Cross",
            "Williams %R Oversold",
            "Williams %R Overbought",
            "CCI Oversold",
            "CCI Overbought",
        ]
    )

    # "Position" requires STRONG fundamentals or CONFIRMED institutional
    # conviction — not just any Piotroski mention or minor institutional flow.
    # Previously, F-Score 3/9 and inst_score=6 would both set position=True,
    # causing 94% of signals to be classified as "position" (wrong style,
    # wrong hold time shown to users, wrong horizon in plain-English summary).
    #
    # New rules — position requires at LEAST one of:
    #   • Piotroski F-Score explicitly ≥7 in the head ("F-Score 7/9" or "8/9" or "9/9")
    #   • Strong FCF yield (already only fires for >8%)
    #   • Active share buyback (management signalling)
    #   • Institutional conviction TREND (QoQ rising/falling — requires 2+ quarters data)
    #   • Very strong institutional flow (score >10, not just >5)
    _is_position = (not _is_intraday) and any(
        kw in _heads_str
        for kw in [
            "F-Score 7",
            "F-Score 8",
            "F-Score 9",  # only high-quality F-scores
            "Strong FCF Yield",
            "Active Share Buyback",
            "Institutional Conviction Rising",  # QoQ trend required
            "Institutional Conviction Falling",
        ]
    )

    _inst_score = abs(((market_ctx or {}).get("institutional_signals") or {}).get(ticker, {}).get("score", 0))
    if _inst_score > 10:
        _is_position = True

    if _is_intraday:
        style = "intraday"
    elif _is_position:
        style = "position"
    else:
        style = "swing"

    # Leveraged/inverse ETFs accumulate volatility-decay drag beyond ~5 days.
    # Position-style hold times are incompatible with daily-rebalancing products.
    if _is_lev_etf and style == "position":
        style = "swing"

    entry, stop, target, rr = _levels(price, atr, action, style, rsi=_rsi_gate)

    # Risk-Free Rate Yield Dampener REMOVED (gate audit 2026-07-14): its
    # cards fired on 76% of the delivered go-forward book (N=323) with
    # ΔWR +0.7pp — a near-universal no-op built on arbitrary constants
    # (3.5/2.0pp sector premiums, ×8 penalty slope) with no ledger entry.
    # Rate context is already carried by the §14 FRED sizing dampener.

    # §64/§65/§66/§68 macro extension gates REMOVED (gate audit 2026-07-14):
    # 0 fires in 87,982 all-time signals — ^TRIN/^NYAD 404 from yfinance so
    # trin/zweig/ad_ema10 never populate (§65/§66), and the §64/§68 T10Y
    # conditions never triggered. Backtest ablation ΔSh=−0.00 for §64/§68.
    # gates/macro_extensions.py deleted; see docs/SIGNAL_VALIDATION.md.

    plain_english = _make_plain_english(action, ticker, style, rationale, confidence, entry, stop, target)

    headline = (
        f"{rationale[0]['head']} · {len(rationale)} signals agree"
        if len(rationale) > 1
        else (rationale[0]["head"] if rationale else f"{action} signal detected")
    )

    # ── XGBoost confidence adjustment (signal model + entry model) ───────
    # Two complementary models blended 50/50 before a single ±25% adjustment:
    #   Signal model  — trained on live DB signals (metadata quality)
    #   Entry model   — trained on 23yr backtest (technical setup quality)
    # Gracefully skipped when models are absent or xgboost is not installed.
    _day_chg_pct = tech.get("change_pct")  # used in ML feature dict below
    _shadow_scores = None
    if action in ("BUY", "SELL"):
        try:
            from services.signal_ml import (
                blend_confidence as _ml_blend,
                get_challenger_model as _get_challenger_model,
                get_model as _get_live_model,
                predict_challenger_prob as _pred_challenger,
                predict_entry_prob_sector as _pred_entry_sector,
                predict_live_prob as _pred_live,
                predict_meta_prob as _pred_meta,
            )

            _live_model = _get_live_model()
            # §93a: decouple static sector lookup from RS fetch — sector-specific
            # entry models were under-applied when RS data failed (81% of signals).
            _sector_etf_ml = (sector_rs or {}).get("sector_etf") or SECTOR_MAP.get(ticker.upper())

            _sig_dict_ml = {
                "raw_score": score,
                "sentiment": avg_sent,
                "sources": list(sources),
                "rationale": rationale,
                "action": action,
                "style": style,
                "rr": rr,
                "entry": entry,
                "stop": stop,
                "target": target,
                "price": price,
                "session": _current_session(),
                "change_pct": _day_chg_pct,
                "days_to_earnings": days_to_earnings,
                "sector_etf": _sector_etf_ml,
                "rs_vs_sector": (sector_rs or {}).get("rs_vs_sector"),
            }
            _live_prob = _pred_live(_sig_dict_ml, _live_model)
            # Use sector-specific entry model when available (XLF/XLP/XLU);
            # falls back to global model automatically via predict_entry_prob_sector.
            _entry_prob = _pred_entry_sector(tech, vix, _sector_etf_ml)
            # A17 challenger: raw_score is already in _sig_dict_ml; model is None
            # until train_challenger_model() clears the AUC delta bar.
            _challenger_prob = _pred_challenger(_sig_dict_ml, _get_challenger_model())
            # Meta-label: P(primary model is correct | context). Uses entry_prob as
            # key input — teaches when the primary signal is reliable.
            _meta_prob = _pred_meta(
                tech,
                _entry_prob,
                (market_ctx or {}).get("hmm_regime"),
                vix,
                _sector_etf_ml,
                days_to_earnings,
                vix_term_ratio=macro.get("vix_term_ratio"),
                sector_momentum=(sector_rs or {}).get("sector_5d_ret"),
                vix_9d_ratio=macro.get("vix_9d_ratio"),
                # §89: FF ST_Rev — fetched daily in backtest; live cache TBD
                ff_str=None,
            )

            if _live_prob is not None or _entry_prob is not None or _challenger_prob is not None:
                confidence = _ml_blend(confidence, _entry_prob, _live_prob, _challenger_prob, _meta_prob)
                if _challenger_prob is not None:
                    _shadow_scores = {
                        "model_id": "A17_challenger",
                        "score": float(_challenger_prob),
                        "confidence": float(confidence),
                        "champion_score": float(_live_prob or 0.0),
                        "champion_confidence": float(confidence),
                    }
        except Exception as _ml_err:
            log.debug("[engine] %s ML blend failed (model may need retraining): %s", ticker, _ml_err)

    # Hard final ceiling — ensures no post-processing step (adaptive weights,
    # yield dampener, factor mining boost) can push confidence above 72%.
    # Empirical calibration (May 2026, n=529): bands 75-84% win at only 48-50%,
    # and 65-70% wins at only 56% — the model's real ceiling of predictive power.
    # _conf_macro_cap re-enforces any active macro contradiction / news-sentiment
    # cap, preventing adaptive win-rate or yield boosts from bypassing it.
    if action in ("BUY", "SELL"):
        confidence = round(min(_conf_macro_cap, max(35.0, confidence)), 1)

    # Final de-confliction safety (string-based warning heads can be brittle):
    # if we detect a known overbought/oversold warning head, apply a small
    # confidence haircut to reduce false-high conviction. This mutates the raw
    # confidence estimate only; calibration (next step) produces the calibrated
    # probability that must remain immutable afterwards.
    confidence = apply_warning_deconfliction(action, confidence, rationale)

    # Persist raw confidence so downstream calibration trains on the pre-calibrated
    # value, avoiding an iterative isotonic-on-isotonic feedback loop.
    raw_confidence = confidence

    # ── MR exit guidance (§35b: RSI45 adaptive exit — 47% hit rate, 100% WR) ──
    # Tells position holders when the mean-reversion bounce is likely complete.
    # Only added for BUY signals with a confirmed MR setup — not for momentum or
    # general BUYs — because the RSI45 threshold was calibrated on MR entries.
    if action == "BUY" and _has_mr:
        _hold_rec = _SECTOR_MR_CONFIG.get(
            (sector_rs or {}).get("sector_etf") or SECTOR_MAP.get(ticker.upper(), ""), {}
        ).get("hold_days", 10)
        rationale = list(rationale) + [
            {
                "src": "Risk Gate",
                "head": "MR Exit Signal: RSI > 45 While Profitable",
                "body": (
                    f"Mean-reversion bounces typically complete when RSI(14) crosses "
                    f"above 45 while the position is profitable (>0.5% gain). "
                    f"20-year backtest: this exit fires on 47% of MR trades at "
                    f"100% win rate, avg +3.0% return. "
                    f"If RSI stays below 45, hold up to {_hold_rec} days while the "
                    f"thesis is intact (price above entry, no stop breach)."
                ),
                "sentiment": "pos",
                "meta": "exit_guidance=rsi45 source=§35b",
            }
        ]

    # ── L8 quality_score — IS-validated MR trade quality composite ───────────
    # Formula: 40%×(score−50)/30 + 35%×OU_speed + 25%×Hurst_MR  → [0, 100]
    # Thresholds recalibrated to IS p67/p33: High(≥43) Sh=0.51 | Mid(35–43) Sh=0.31 | Low(<35) Sh=0.17
    # All three inputs are already in tech dict — zero extra API cost.
    _ou_hl_qs = float(tech.get("ou_halflife") or 12.5)
    _hurst_qs_raw = tech.get("hurst")
    _hurst_qs = (
        float(_hurst_qs_raw) if isinstance(_hurst_qs_raw, (int, float)) and math.isfinite(_hurst_qs_raw) else 0.65
    )
    _quality_score = min(
        100.0,
        max(
            0.0,
            min(40.0, (score - 50.0) / 30.0 * 40.0)
            + 35.0 * max(0.0, 1.0 - _ou_hl_qs / 25.0)
            + 25.0 * max(0.0, 1.0 - (_hurst_qs - 0.5) / 0.30),
        ),
    )

    # ── L9 HMM regime vars — sourced from macro_regime.py (1h cache) ─────────
    _hmm_ctx = (market_ctx or {}).get("hmm_regime", {})
    _hmm_regime_label = _hmm_ctx.get("regime", "")
    _hmm_bear_prob = float(_hmm_ctx.get("bear_prob", 0.5))
    _hmm_bull_prob = float(_hmm_ctx.get("bull_prob", 0.5))
    _hmm_trans_risk = float(_hmm_ctx.get("transition_risk", 0.1))

    # ── L11 §14 FRED macro-regime dampener (re-instated 2026-06-12) ──────────
    # The 06-10 deletion of §14 delivery hard blocks cited a −0.06 A/B that ran
    # while a FRED realtime_start bug had emptied the panel (LEARNINGS 2026-06-12).
    # Two consistent working-panel reads (+0.02 / +0.03 Sh, MaxDD −2.31%→−0.93%)
    # support the gate. Per house doctrine it returns as a SIZING tilt, never a
    # block, pending forward SPRT confirmation (scripts/sprt_preregister_fred_regime.py).
    # Thresholds mirror the backtest §14 gate: marginal = NFCI>0 / Baa−10Y>3% /
    # inverted 10Y−3M (dampens only marginal-score BUYs); extreme = NFCI>0.5 / Baa−10Y>4%.
    _nfci_v = macro.get("nfci") if macro else None
    _baa10y_v = macro.get("baa10y") if macro else None
    _t10y3m_v = macro.get("t10y3m") if macro else None
    _fred_regime_mult = 1.0
    if action == "BUY":
        _fred_extreme = (_nfci_v is not None and _nfci_v > 0.5) or (_baa10y_v is not None and _baa10y_v > 4.0)
        _fred_marginal = (
            (_nfci_v is not None and _nfci_v > 0.0)
            or (_baa10y_v is not None and _baa10y_v > 3.0)
            or (_t10y3m_v is not None and _t10y3m_v < 0.0)
        )
        if _fred_extreme:
            _fred_regime_mult = 0.75
        elif _fred_marginal and score < 55:
            _fred_regime_mult = 0.85
    if _fred_regime_mult < 1.0:
        rationale.append(
            {
                "src": "Macro Regime",
                "head": f"§14 FRED regime dampener: sizing ×{_fred_regime_mult:.2f}",
                "body": (
                    "Credit/financial-conditions regime is tight "
                    f"(NFCI={_nfci_v if _nfci_v is not None else 'n/a'}, "
                    f"Baa−10Y={_baa10y_v if _baa10y_v is not None else 'n/a'}, "
                    f"10Y−3M={_t10y3m_v if _t10y3m_v is not None else 'n/a'}). "
                    "Backtest: blocking these regimes improves Sharpe +0.03 and cuts MaxDD "
                    "−2.31%→−0.93%; applied live as a position-size reduction, never a block, "
                    "pending forward SPRT validation."
                ),
                "sentiment": "neg",
                "meta": f"sizing_tilt=fred_regime_dampener mult={_fred_regime_mult}",
            }
        )

    # ── Calibration as the LAST confidence-mutating step ────────────────────
    # QUANT_ENGINE_REVIEW §1.4 / §5 Snippet 8: calibration was previously applied
    # *before* ML blend, overbought haircuts, and peer haircut — but trained on
    # the *final stored* confidence.  This created an iterative feedback loop.
    # Now calibration sees the fully-mutated raw confidence and produces the
    # calibrated probability of winning.  From this point forward
    # `calibrated_probability` must never be mutated; only `display_confidence`
    # (user-facing) and `positionSizeScale` may be adjusted by post-scan context.
    calibrated_probability = confidence
    if action in ("BUY", "SELL"):
        from services.calibration import apply_calibration

        cal_map = (market_ctx or {}).get("calibration_map", {})
        if cal_map:
            pre_cal = calibrated_probability
            _sp500_trend = macro.get("sp500_trend") if macro else None
            _cal_regime = "bull" if _sp500_trend == "up" else "bear" if _sp500_trend == "down" else "neutral"
            _cal_sector = (sector_rs or {}).get("sector_etf") or SECTOR_MAP.get(ticker.upper())
            calibrated_probability, _bin = apply_calibration(
                calibrated_probability, action, cal_map, regime=_cal_regime, sector=_cal_sector
            )
            if _bin and abs(calibrated_probability - pre_cal) >= 2:
                _source = _bin.get("source", "platt")
                _emp_wr = round((_bin.get("win_rate") or _bin.get("prob", pre_cal / 100)) * 100, 1)
                _n = _bin.get("n", 0)
                _blend = round((_bin.get("blend", 0)) * 100)
                _gap = round(_emp_wr - pre_cal, 1)
                _bin_lo = (int(pre_cal) // 5) * 5
                _bin_hi = _bin_lo + 5
                _dir = "DOWN" if calibrated_probability < pre_cal else "UP"
                _over = calibrated_probability < pre_cal
                _is_iso = "isotonic" in _source

                if _is_iso:
                    _body = (
                        f"Isotonic regression ({_source}) mapped {pre_cal:.0f}% → {calibrated_probability:.0f}%. "
                        f"Empirical win rate at this confidence level: {_emp_wr:.0f}%. "
                        f"The model is {'over' if _over else 'under'}confident by {abs(_gap):.0f}pp "
                        f"in this confidence region based on resolved signal history."
                    )
                    _meta = f"source={_source} | EmpWR: {_emp_wr:.0f}%"
                else:
                    _body = (
                        f"The model assigned {pre_cal:.0f}% confidence, but {_n} resolved "
                        f"{action} signals in the {_bin_lo}–{_bin_hi}% band have an actual "
                        f"win rate of {_emp_wr:.0f}% — a {abs(_gap):.0f}pp "
                        f"{'overconfidence' if _over else 'underconfidence'} gap. "
                        f"Confidence blended {_blend}% toward the empirical rate."
                    )
                    _meta = (
                        f"Bin {_bin_lo}–{_bin_hi}% | "
                        f"Empirical WR: {_emp_wr:.0f}% | "
                        f"n={_n} signals | "
                        f"Blend: {_blend}% empirical + {100 - _blend}% model"
                    )

                rationale.append(
                    {
                        "src": "Backtest",
                        "head": (
                            f"Calibration {_dir}: {pre_cal:.0f}% → {calibrated_probability:.0f}%"
                            f" ({'overconfident' if _over else 'underconfident'} by {abs(_gap):.0f}pp)"
                        ),
                        "body": _body,
                        "sentiment": "pos" if not _over else "neg",
                        "meta": _meta,
                    }
                )
            # Re-apply hard ceiling after calibration so no post-calibration value
            # escapes the empirical cap.
            calibrated_probability = round(min(_conf_macro_cap, max(35.0, calibrated_probability)), 1)

    # Display confidence starts from the calibrated probability.  Post-scan steps
    # (peer confirmation, cross-sectional ranking, etc.) may tilt this value for
    # display/sizing purposes but must never mutate calibrated_probability.
    display_confidence = calibrated_probability

    # Calibration warning: fires when the calibrated probability significantly
    # exceeds the historically observed win rate for this action type, or when
    # strong conflicting signals were penalised away but confidence still appears
    # high to the user.  Kept on the evidence-based calibrated probability.
    if action in ("BUY", "SELL") and calibrated_probability >= 75:
        win_rate_hist = (adaptive or {}).get(f"{action}_win_rate")
        if (
            win_rate_hist is not None
            and calibrated_probability - win_rate_hist * 100 > 20
            or total_confidence_penalty >= 0.15
        ):
            confidence_warning = True
    else:
        confidence_warning = False

    return {
        "ticker": ticker,
        "company": info.get("company", ticker),
        "action": action,
        "alphaScore": score,
        "raw_score": score,
        "rawConfidence": raw_confidence,
        "raw_confidence": raw_confidence,
        "calibratedProbability": calibrated_probability,
        "displayConfidence": display_confidence,
        # Backward-compatible alias: old consumers expect a single `confidence`
        # field.  It now equals the user-facing display confidence, which may
        # include post-scan peer/ranking tilts.
        "confidence": display_confidence,
        "confidence_warning": confidence_warning,
        "rankScore": None,
        "rankPercentile": None,
        "price": price,
        "change": tech.get("change", 0),
        "changePct": tech.get("change_pct", 0),
        "entry": entry,
        "stop": stop,
        "target": target,
        "rr": rr,
        "headline": headline,
        "sentiment": round(avg_sent, 2),
        "style": style,
        "sources": sorted(sources),
        "rationale": rationale,
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "session": _current_session(),
        "daysToEarnings": days_to_earnings,
        "daysToExDiv": days_to_exdiv,
        "nextEarningsDate": earnings_cal.get("next_earnings_date"),
        # sector_etf is a static SECTOR_MAP lookup — always populate it even when
        # the relative-strength fetch failed (sector_rs is None). Decoupling these
        # keeps the audit tag and the BLOCKED_SECTORS delivery gate working; only
        # the RS *metrics* below go null when live data is unavailable.
        "sectorEtf": (sector_rs["sector_etf"] if sector_rs else SECTOR_MAP.get(ticker.upper())),
        "rsVsSector": sector_rs["rs_vs_sector"] if sector_rs else None,
        "plain_english": plain_english,
        "beta": info.get("beta"),
        "dataWarnings": data_warnings,
        "positionSizeScale": round(
            # §QuantEngine sizing stack (nine layers):
            # L1 portfolio_size_scale — sector concentration + PCA cross-sector (§43/§83)
            # L2 VIX-regime overlay   — fear 1.15×/panic 1.10×/calm 0.75× (§56)
            # L3 vol-targeting        — 0.25/ticker_vol_ann clamped [0.5,2.0]
            # L4 conviction sizing    — (conf-40)/14+0.5 clamped [0.5,1.5]
            #    conf=40→0.5×  conf=47→1.0×  conf=54+→1.5× (anchored to min_confidence=40)
            # L5 gate-quality boost   — Inv3: Hurst+20.6pp, Piotroski+13.1pp, IVR+10.1pp
            #    fires only for BUY; caps at 1.5× total; rewards best-predictor gates
            # L6 regime dampener      — calm bull (VIX<18 + bull trend) reduces MR sizing 0.8×
            #    AI-momentum regimes produce shallow bounces; Inv2+temporal: current regime weak
            # L7 raw-score Kelly      — §18/§12a: non-linear score-band sizing (backtest-validated).
            #    <50→0.50×  50-55→0.75×  55-60→1.00×  60-65→1.15×  65-70→1.30×  70-75→1.45×  ≥75→1.55×
            # L8 quality_score tier   — IS Sh spread High(≥43) 0.51 vs Low(<35) 0.17, v10.1 2026-06-01
            #    high(≥43)→1.30× mid(35–43)→1.0× low(<35)→0.75×; zero N impact (all trades pass)
            # L9 HMM regime sizing    — macro_regime.py 2-state Baum-Welch leads VIX by 1-3d
            #    IS ablation: bull 1.10× never fires on MR entries (low-VIX = no MR triggers)
            #    bear(≥80%)→0.70× transition/trans_risk>20%→0.85× bull→1.0× (no amplification)
            #    MaxDD confirmed: 0.86→0.73 from transition dampener (ablation 2026-06-01)
            portfolio_size_scale
            * (
                1.15
                if (vix is not None and 20 <= vix <= 30 and confidence >= 58)
                else 1.10
                if (vix is not None and vix > 30 and confidence >= 55)
                else 0.75
                if (vix is not None and vix < 15)
                else 1.0
            )
            * (
                max(0.5, min(2.0, 0.25 / max(_atr_pct_pre * _np.sqrt(252), 0.05)))
                * max(0.5, min(1.5, (confidence - 40.0) / 14.0 + 0.5))
                * min(
                    1.5,
                    # L5: gate-quality — multiply for each high-predictor gate that fired
                    (
                        1.20
                        if any("Hurst" in c.get("head", "") and c.get("sentiment") == "pos" for c in rationale)
                        else 1.0
                    )
                    * (
                        1.15
                        if any("Piotroski" in c.get("head", "") and c.get("sentiment") == "pos" for c in rationale)
                        else 1.0
                    )
                    * (
                        1.10
                        if any(
                            ("IVR" in c.get("head", "") or "IV Rank" in c.get("head", ""))
                            and c.get("sentiment") == "pos"
                            for c in rationale
                        )
                        else 1.0
                    ),
                )
                * (
                    # L6: calm-bull regime dampener (AI-rally / low-VIX momentum)
                    0.80
                    if (
                        vix is not None
                        and vix < 18
                        and (macro or {}).get("sp500_trend") == "up"
                        and (macro or {}).get("macro_score", 0) > 3
                    )
                    else 1.0
                )
                * (  # L7 raw-score Kelly — §18/§12a: non-linear score-band sizing (backtest-validated)
                    1.55
                    if score >= 75
                    else 1.45
                    if score >= 70
                    else 1.30
                    if score >= 65
                    else 1.15
                    if score >= 60
                    else 1.00
                    if score >= 55
                    else 0.75
                    if score >= 50
                    else 0.50
                )
                # L8: quality_score tier — thresholds recalibrated 2026-06-01 to IS p67/p33.
                # IS distribution: High(≥43) N=63 Sh=0.51 | Mid(35–43) N=63 Sh=0.31 | Low(<35) N=62 Sh=0.17
                # Old thresholds (60/30) put 80% in Mid (neutral) → no lift. Corrected to (43/35).
                * (1.30 if _quality_score >= 43 else 0.75 if _quality_score < 35 else 1.0)
                # L9: HMM regime sizing — transition dampener only (2026-06-01 fix)
                # Bear dampener REMOVED: IS ablation shows bear WR=72% > baseline 70.7%.
                # HMM "bear" fires on highest-VIX periods — exactly when MR bounces are strongest
                # (deepest fear = deepest overselling = most reliable 10d recovery). Sizing DOWN
                # in these periods cut our best trades. Fix: bear → 1.0× (neutral).
                # Transition dampener KEPT: MaxDD 0.86% → 0.73% confirmed (regime uncertainty
                # = incomplete information = appropriate size reduction).
                * (0.85 if (_hmm_regime_label == "transition" or _hmm_trans_risk > 0.20) else 1.0)
                # L11: §14 FRED macro-regime dampener — re-instated 2026-06-12 as a
                # sizing tilt (the 06-10 hard-block deletion cited a dead-panel A/B).
                * _fred_regime_mult
                if action == "BUY"
                else 1.0
            ),
            2,
        ),
        "recommendedHoldDays": (
            _SECTOR_MR_CONFIG.get((sector_rs or {}).get("sector_etf") or SECTOR_MAP.get(ticker.upper(), ""), {}).get(
                "hold_days", 10
            )
            if _has_mr
            else 10
        ),
        "vix": vix,
        "crossAssetHeadwinds": macro.get("cross_asset_headwinds"),
        "nfci": macro.get("nfci"),
        "baa10y": macro.get("baa10y"),
        "t10y3m": macro.get("t10y3m"),
        # L11 §14 dampener multiplier — SPRT population selector (1.0 = regime clean)
        "fredRegimeDampener": _fred_regime_mult,
        # §82: trailing stop as % of entry — 2× ATR provides dynamic stop that adapts
        # to realized vol and avoids being stopped out by normal intraday noise.
        "trailingStopPct": round(atr / price * 200, 2) if (price and atr and price > 0) else None,
        # L8: quality_score tier for live tracking and hard-gate research
        "qualityScore": round(_quality_score, 1),
        # L9: HMM regime label for frontend display and future hard-gate research
        "hmmRegime": _hmm_regime_label or None,
        # ATR%rank — delivery_gates uses this for ATR≤70 quality gate (trend-dominant regime check)
        "atrPctRank": round(float(tech.get("atr_pct_rank") or 50), 1),
        # MR setup flag — delivery_gates enforces this as a hard BUY gate.
        # True = at least TWO of: RSI<42, BB%B<0.22, IBS<0.15, VWAP%<-0.75%.
        # Changed from 1→2 on 2026-06-09: backtest showed MR-count=2 improves
        # Sharpe 0.20→0.21 with only -1 trade (154 vs 155). Single-condition
        # MR setups (especially IBS-only) are the weakest class.
        # Without this flag the live engine issues BUYs on uptrending stocks
        # (Golden Cross, Above 200-DMA, EPS beats) that have never been validated
        # in the 23-year backtest, producing live WR ≈42% vs backtest WR ≈68%.
        "hasMr": _has_mr,
        # SELL MR setup flag — delivery_gates enforces this when LONG_ONLY=false.
        # True = at least one of: RSI>58, BB%B>0.78, IBS>0.85, VWAP%>0.75%.
        "hasMrSell": _has_mr_sell,
        # ALPHA-5: VIX regime tag — informational; used by per-regime WR audit (gate_contribution_analysis.py --sector-wr)
        # after N≥100 resolved signals per regime. Not a delivery gate yet.
        "vixRegime": (
            "stress"
            if (vix is not None and vix >= 30)
            else "elevated"
            if (vix is not None and vix >= 20)
            else "calm"
            if vix is not None
            else "unknown"
        ),
        "_ticker_perf_shadow": (
            {
                **_ticker_perf_shadow,
                "hold_days": (
                    _SECTOR_MR_CONFIG.get(
                        (sector_rs or {}).get("sector_etf") or SECTOR_MAP.get(ticker.upper(), ""), {}
                    ).get("hold_days", 10)
                    if _has_mr
                    else 10
                ),
            }
            if _ticker_perf_shadow is not None
            else None
        ),
        "gate_traces": _sig_ctx.gate_traces,
        "shadow_scores": _shadow_scores,
        "features": {
            **tech,
            "vix": vix,
            "sp500_trend": sp500_trend,
            "quality_score": _quality_score,
            "hasMr": _has_mr,
            "hasMrSell": _has_mr_sell,
            "vix_term_ratio": macro.get("vix_term_ratio"),
            "vix_9d_ratio": macro.get("vix_9d_ratio"),
            "sector_momentum": (sector_rs or {}).get("sector_5d_ret"),
        },
    }
