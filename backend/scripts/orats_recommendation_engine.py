#!/usr/bin/env python3
"""ORATS fusion recommendation engine — standalone (does NOT modify the live engine).

Fuses three validated views into one concrete action per name:

  1. DIRECTION  — the live signal engine's BUY/SELL/HOLD (read from the `signals`
     table). This is where the tech mean-reversion edge lives; for names the engine
     does not cover, there is simply no directional view.
  2. VOLATILITY / VRP — the ORATS move-size forecast vs the option-implied move
     (`orats_opportunity_model.get_vol_view`). richness = implied / forecast; rich
     ⇒ options overprice the move (sell premium), cheap ⇒ underprice (buy premium).
     Validated edge: rich-decile premium-seller ≈ +3%/2d (companies), ≈ +4.5% (ETF).
  3. EVENT RISK — days-to-earnings (from `signals`, else yfinance). Rich IV that is
     really a binary earnings event is NOT a variance-risk-premium to harvest, so
     premium-selling is suppressed into earnings.

Action vocabulary (the "what to do"):
  BUY_STOCK            directional BUY, options not rich (buy shares / long calls if cheap)
  SELL_CASH_SEC_PUT    directional BUY + rich options → get paid to enter
  SELL_STRANGLE        no direction + rich options + no earnings → pure VRP harvest (single names)
  SELL_DEFINED_RISK    index mode: rich index options → iron condor / put spread (never naked)
  LONG_STRADDLE        cheap options + a known catalyst → buy the move (speculative)
  AVOID_EARNINGS       rich IV driven by imminent earnings → stand aside
  NO_ACTION            no directional edge and options fairly priced

Universes (--universe): companies (CS/ADRC ≥$10B), etf (≥$1B AUM), index (broad-market/
sector index ETFs only — the VIX-analog market VRP; thinner edge, undiversifiable tail,
defined-risk structures only; gate on the VIX/VIX3M term structure before sizing).

Usage:
    cd backend && python scripts/orats_recommendation_engine.py                  # companies, next 2 days
    cd backend && python scripts/orats_recommendation_engine.py --universe etf
    cd backend && python scripts/orats_recommendation_engine.py --universe index  # market-level VRP (VIX analog)
    cd backend && python scripts/orats_recommendation_engine.py --horizon 3 --top-n 30

Output:
    - console action table (validation header + per-name recommendations)
    - data/orats_recommendations_<universe>_<date>.csv
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path

import pandas as pd

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.orats_opportunity_model import get_vol_view  # noqa: E402

log = logging.getLogger("signal.orats_recommendation_engine")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# 'Rich' = top-quintile richness (implied/forecast) AND richness > 1; see _decide for
# why 'cheap' is an absolute (richness < 1) test rather than a bottom percentile.
_RICH_PCT = 0.80

# Trade-plan params. ATM straddle premium ≈ 0.8× the 1σ implied move; sizing is by a
# risk budget with a hard per-trade concentration cap (premium-selling tail is real and
# untested, so caps are deliberately tight).
_STRADDLE_PREMIUM_FRAC = 0.80
_CONC_CAP = {  # max underlying notional per trade as a fraction of capital
    "SELL_STRANGLE": 0.05,
    "SELL_DEFINED_RISK": 0.05,
    "SELL_CASH_SEC_PUT": 0.08,
    "BUY_STOCK": 0.10,
    "LONG_STRADDLE": 0.02,
}


def _cdf(ratio_q: list[float], x: float) -> float:
    """P(realized/forecast move ≤ x) from the empirical quantile grid."""
    if not ratio_q:
        return float("nan")
    import numpy as np

    return float(np.searchsorted(ratio_q, x) / (len(ratio_q) - 1))


def _trade_plan(row: pd.Series, ratio_q: list[float], capital: float, risk_per_trade: float) -> dict:
    """Per-recommendation win probability, position size, expected gain, max loss.

    Estimates come from the in-sample (no-vol-spike) move distribution — win prob is
    optimistic on the tail. All P&L is per the *underlying* notional the options cover."""
    act = row["action"]
    px = row["stk_px"]
    impl = row["impl_move"]
    fcst = row["forecast_move"]
    premium = _STRADDLE_PREMIUM_FRAC * impl  # fraction of underlying
    breakeven_mult = (premium / fcst) if fcst > 0 else float("nan")  # breakeven in forecast-move units
    budget = risk_per_trade * capital

    if act in ("SELL_STRANGLE", "SELL_DEFINED_RISK"):
        win = _cdf(ratio_q, breakeven_mult)  # win if realized < premium
        edge = premium - fcst  # E[P&L] = collect premium, pay expected realized move
        risk = 3.0 * premium  # tail-capped stop (defined-risk caps at the spread width)
    elif act == "SELL_CASH_SEC_PUT":
        two_sided = _cdf(ratio_q, breakeven_mult)
        win = two_sided + (1 - two_sided) / 2  # one-sided: only a down move hurts a put seller
        edge = premium - 0.5 * fcst
        risk = 3.0 * premium
    elif act == "LONG_STRADDLE":
        win = 1 - _cdf(ratio_q, breakeven_mult)  # win if realized > premium paid
        edge = fcst - premium
        risk = premium  # max loss = premium paid
    elif act == "BUY_STOCK":
        conf = row.get("dir_confidence")
        win = (conf / 100.0) if conf and pd.notna(conf) else float("nan")
        ent, tgt, stp = row.get("dir_entry"), row.get("dir_target"), row.get("dir_stop")
        edge = ((tgt - ent) / ent) if ent and tgt and ent > 0 else fcst
        risk = ((ent - stp) / ent) if ent and stp and ent > 0 else 0.5 * impl
    else:
        return {"win_prob": float("nan"), "notional": 0.0, "exp_gain": 0.0, "max_loss": 0.0, "units": 0.0}

    risk = max(risk, 0.005)
    notional = min(budget / risk, _CONC_CAP.get(act, 0.05) * capital)
    units = notional / px if act == "BUY_STOCK" else notional / (100 * px)  # shares vs option contracts
    return {
        "win_prob": win,
        "notional": notional,
        "exp_gain": edge * notional,
        "max_loss": risk * notional,
        "units": units,
    }


_ACTIONABLE = {"BUY_STOCK", "SELL_CASH_SEC_PUT", "SELL_STRANGLE", "SELL_DEFINED_RISK", "LONG_STRADDLE"}


def build_book(
    df: pd.DataFrame, capital: float, max_book_risk: float, max_positions: int, max_iv_sell: float
) -> pd.DataFrame:
    """Construct the actual portfolio: rank actionable recs by reward/risk, exclude
    extreme-IV names from the sell side (leveraged ETFs / blowup risk), then greedily
    add until total premium-at-risk hits the book cap. This bounds the correlated
    worst case (sum of max_loss ≤ cap) — the thing that destroys naive short-vol books."""
    a = df[df["action"].isin(_ACTIONABLE)].copy()
    is_sell = a["action"].str.startswith("SELL")
    a = a[~(is_sell & (a["atm_iv_30d"] > max_iv_sell))]  # drop leveraged/extreme-IV from sells
    a = a[a["max_loss"] > 0]
    a["reward_risk"] = a["exp_gain"] / a["max_loss"].clip(lower=1.0)
    a = a.sort_values(["reward_risk", "win_prob"], ascending=False)

    budget = max_book_risk * capital
    chosen, risk = [], 0.0
    for _, r in a.iterrows():
        if len(chosen) >= max_positions:
            break
        if risk + r["max_loss"] > budget:
            continue
        chosen.append(r)
        risk += r["max_loss"]
    return pd.DataFrame(chosen)


async def _load_direction_view() -> pd.DataFrame:
    """Latest active directional signal per ticker from the live engine's `signals`
    table, plus its earnings fields. Empty frame if the table has nothing."""
    from sqlalchemy import select

    from database import AsyncSessionLocal, engine
    from models import Signal

    # get_vol_view ran its own asyncio.run() (now-closed loop); the engine pool is
    # bound to that dead loop. Dispose so it rebuilds on the current loop.
    await engine.dispose()

    async with AsyncSessionLocal() as db:
        rows = (
            (
                await db.execute(
                    select(Signal).where(Signal.is_active.is_(True)).order_by(Signal.ticker, Signal.created_at.desc())
                )
            )
            .scalars()
            .all()
        )

    seen: dict[str, dict] = {}
    for r in rows:
        if r.ticker in seen:  # first row per ticker = most recent (desc order)
            continue
        seen[r.ticker] = {
            "ticker": r.ticker,
            "dir_action": r.action,
            "dir_confidence": r.confidence,
            "dir_score": r.raw_score,
            "dir_entry": r.entry,
            "dir_stop": r.stop,
            "dir_target": r.target,
            "days_to_earnings": r.days_to_earnings,
            "next_earnings_date": r.next_earnings_date,
        }
    return pd.DataFrame(list(seen.values()))


async def _earnings_for(tickers: list[str]) -> dict[str, int | None]:
    """days_to_earnings for tickers missing it, via the existing yfinance calendar
    service. Concurrency-limited; failures map to None (treated as 'no known event')."""
    from services.earnings import get_earnings_calendar

    sem = asyncio.Semaphore(8)

    async def one(t: str):
        async with sem:
            try:
                cal = await get_earnings_calendar(t)
                return t, cal.get("days_to_earnings")
            except Exception:
                return t, None

    out = await asyncio.gather(*[one(t) for t in tickers])
    return dict(out)


def _decide(row: pd.Series, horizon: int) -> tuple[str, str]:
    """Map a fused row to (action, rationale)."""
    d = row.get("dir_action")
    # The VRP is near-universal (almost every name has implied > forecast), so 'rich'
    # is the richest quintile, but 'cheap' must be ABSOLUTE (implied actually below
    # forecast, richness < 1) — a bottom-percentile name with richness 1.2 is still
    # overpriced, not a buy-premium candidate.
    rich = row["richness_pct"] >= _RICH_PCT and row["richness"] > 1.0
    cheap = row["richness"] < 1.0
    dte = row.get("days_to_earnings")
    earn_soon = dte is not None and pd.notna(dte) and 0 <= dte <= horizon + 1
    impl = row["impl_move"] * 100
    fcst = row["forecast_move"] * 100

    if earn_soon and rich:
        if d == "BUY":
            return (
                "BUY_STOCK",
                f"Directional BUY but earnings in {int(dte)}d — buy shares, do NOT sell premium into the event",
            )
        return (
            "AVOID_EARNINGS",
            f"Rich IV (implied {impl:.1f}% vs forecast {fcst:.1f}%) is an earnings event in {int(dte)}d, not a VRP",
        )

    if d == "BUY" and rich:
        return (
            "SELL_CASH_SEC_PUT",
            f"Engine BUY + rich options (implied {impl:.1f}% > forecast {fcst:.1f}%) → get paid to enter",
        )
    if d == "BUY" and cheap:
        return (
            "BUY_STOCK",
            f"Engine BUY + cheap options (implied {impl:.1f}% < forecast {fcst:.1f}%) → buy shares / long calls",
        )
    if d == "BUY":
        return ("BUY_STOCK", f"Engine BUY, options fairly priced (implied {impl:.1f}%)")

    if rich and not earn_soon:
        return (
            "SELL_STRANGLE",
            f"No directional edge + rich options (implied {impl:.1f}% > forecast {fcst:.1f}%) → harvest VRP",
        )
    if cheap and not earn_soon:
        return (
            "LONG_STRADDLE",
            f"Cheap options (implied {impl:.1f}% < forecast {fcst:.1f}%) — buy the move only if a catalyst is expected",
        )
    return ("NO_ACTION", "No directional edge and options fairly priced")


# Sort priority for the printed/saved action list.
_ACTION_ORDER = {
    "SELL_CASH_SEC_PUT": 0,
    "BUY_STOCK": 1,
    "SELL_DEFINED_RISK": 2,
    "SELL_STRANGLE": 2,
    "LONG_STRADDLE": 3,
    "AVOID_EARNINGS": 4,
    "NO_ACTION": 5,
}

# Broad-market + sector index ETFs for the `index` mode (the market-level VRP, the VIX
# analog). Trained on the full ETF universe, then filtered to these. NB: on a single
# index the VRP is thinner and the tail is undiversifiable (SPY realized/implied mean
# 0.93 vs 0.72 cross-sectional) → recommend DEFINED-RISK structures, never naked.
_INDEX_ETFS = {
    "SPY",
    "VOO",
    "IVV",
    "QQQ",
    "QQQM",
    "IWM",
    "DIA",
    "MDY",
    "RSP",
    "VTI",
    "EFA",
    "EEM",
    "VEA",
    "VWO",
    "ACWI",
    "XLK",
    "XLF",
    "XLE",
    "XLV",
    "XLI",
    "XLP",
    "XLU",
    "XLY",
    "XLB",
    "XLC",
    "XLRE",
}


def main() -> None:
    ap = argparse.ArgumentParser(description="ORATS fusion recommendation engine")
    ap.add_argument(
        "--universe",
        choices=["companies", "etf", "index"],
        default="companies",
        help="index = broad-market/sector index ETFs only (the VIX-analog market VRP; defined-risk structures)",
    )
    ap.add_argument("--horizon", type=int, default=2, help="Trading-day horizon for the vol/VRP view (default 2)")
    ap.add_argument("--model", choices=["xgb", "ridge"], default="xgb", help="vol forecaster (xgb best for move-size)")
    ap.add_argument("--top-n", type=int, default=25, help="Rows to print per actionable bucket")
    ap.add_argument("--min-opt-volume", type=float, default=500.0)
    ap.add_argument("--capital", type=float, default=100_000.0, help="Account size for sizing (default $100k)")
    ap.add_argument(
        "--risk-per-trade",
        type=float,
        default=0.01,
        help="Risk budget per trade as a fraction of capital (default 1%%)",
    )
    ap.add_argument(
        "--max-book-risk",
        type=float,
        default=0.10,
        help="Cap on TOTAL premium-at-risk across the book as a fraction of capital (default 10%%)",
    )
    ap.add_argument("--max-positions", type=int, default=20, help="Max positions in the recommended book")
    ap.add_argument(
        "--max-iv-sell",
        type=float,
        default=0.80,
        help="Exclude names with ATM IV above this from the SELL side (leveraged ETFs / blowup risk)",
    )
    ap.add_argument("--no-earnings-fetch", action="store_true", help="Skip yfinance earnings backfill (faster)")
    ap.add_argument("--output-dir", default="data")
    args = ap.parse_args()

    # 'index' trains on the full ETF universe (more data) then scores only index ETFs.
    is_index = args.universe == "index"
    vol_universe = "etf" if is_index else args.universe

    log.info("Computing ORATS volatility/VRP view (%s, horizon=%dd)…", args.universe, args.horizon)
    summary, vol = get_vol_view(
        universe=vol_universe, horizon=args.horizon, model_name=args.model, min_opt_volume=args.min_opt_volume
    )
    if is_index:
        vol = vol[vol["ticker"].isin(_INDEX_ETFS)].reset_index(drop=True)
        log.info("Index mode: filtered to %d broad-market/sector index ETFs", len(vol))

    log.info("Loading live directional signals from DB…")
    direction = asyncio.run(_load_direction_view())
    n_dir = 0 if direction.empty else (direction["dir_action"].isin(["BUY", "SELL"]).sum())
    log.info("Direction view: %d signals (%d BUY/SELL)", len(direction), n_dir)

    df = (
        vol.merge(direction, on="ticker", how="left")
        if not direction.empty
        else vol.assign(
            dir_action=None,
            dir_confidence=None,
            dir_score=None,
            dir_entry=None,
            dir_stop=None,
            dir_target=None,
            days_to_earnings=None,
            next_earnings_date=None,
        )
    )

    # Backfill earnings for the names that will plausibly get a premium action (rich
    # or directional BUY) and are missing days_to_earnings — that's where it matters.
    if not args.no_earnings_fetch:
        need = df[(df["days_to_earnings"].isna()) & ((df["richness_pct"] >= _RICH_PCT) | (df["dir_action"] == "BUY"))][
            "ticker"
        ].tolist()
        if need:
            log.info("Backfilling earnings dates for %d candidate names…", len(need))
            dte_map = asyncio.run(_earnings_for(need))
            df["days_to_earnings"] = df.apply(
                lambda r: dte_map.get(r["ticker"]) if pd.isna(r["days_to_earnings"]) else r["days_to_earnings"],
                axis=1,
            )

    actions = df.apply(lambda r: _decide(r, args.horizon), axis=1)
    df["action"] = [a for a, _ in actions]
    df["rationale"] = [w for _, w in actions]
    if is_index:
        # Naked strangles are inappropriate on an index — the tail is market-wide and
        # undiversifiable (this is exactly what blows up short-VIX). Use defined risk.
        m = df["action"] == "SELL_STRANGLE"
        df.loc[m, "action"] = "SELL_DEFINED_RISK"
        df.loc[m, "rationale"] = df.loc[m, "rationale"].str.replace(
            "→ harvest VRP",
            "→ sell DEFINED-RISK premium (iron condor / put spread), never naked — index tail is undiversifiable",
            regex=False,
        )
    # Per-recommendation trade plan: win probability, size, expected gain, max loss.
    plan = df.apply(lambda r: _trade_plan(r, summary.get("ratio_q", []), args.capital, args.risk_per_trade), axis=1)
    plan_df = pd.DataFrame(list(plan), index=df.index)
    df = pd.concat([df, plan_df], axis=1)

    df["action_rank"] = df["action"].map(_ACTION_ORDER)
    df = df.sort_values(["action_rank", "richness"], ascending=[True, False])

    # ── Report ──
    print("\n" + "=" * 78)
    print(
        f"  ORATS FUSION RECOMMENDATIONS — {args.universe} — next {args.horizon} trading days — {summary['latest_date']}"
    )
    print("=" * 78)
    print(
        f"  Vol forecast IC {summary['forecast_ic']:+.2f} | realized/implied move {summary['vrp_mean']:.2f} "
        f"| premium-seller base rate {summary['pct_below'] * 100:.0f}%"
    )
    print(
        f"  Validated rich-decile seller edge {summary['rich_edge'] * 100:+.2f}%/trade "
        f"(spread vs cheap {(summary['rich_edge'] - summary['cheap_edge']) * 100:+.2f}%)"
    )
    bt = summary.get("straddle_bt") or {}
    if bt:
        print(
            f"  Tail-capped short-straddle P&L: net {bt['mean_net'] * 100:+.2f}%/trade, win {bt['win_rate'] * 100:.0f}%, "
            f"Sharpe {bt['sharpe_ann']:+.1f}, worst {bt['worst'] * 100:+.0f}%, hit-cap {bt['pct_hit_cap'] * 100:.0f}%"
        )
        if bt.get("pct_hit_cap") == 0:
            print("    ⚠ hit-cap 0% ⇒ this 5-month sample has NO vol spike; short-vol tail risk is UNTESTED here.")
    print(f"  Directional signals fused: {n_dir} BUY/SELL from the live engine")
    print(
        f"  Sizing: capital ${args.capital:,.0f}, risk budget {args.risk_per_trade * 100:.1f}%/trade; "
        "win% & $ are model estimates from a no-vol-spike sample (optimistic on the tail)."
    )
    if is_index:
        print("  ⚠ INDEX/VIX-analog mode — market-level VRP is THINNER & tail is undiversifiable")
        print("    (SPY realized/implied mean ~0.93 vs 0.72 cross-sectional). Use DEFINED-RISK structures,")
        print("    NOT VIX ETPs (VXX/UVXY/SVXY add roll-decay/leverage this data can't price), and gate on")
        print("    the VIX/VIX3M term structure (live macro.py §47) — flatten when it inverts (backwardation).")
    print("=" * 78)

    counts = df["action"].value_counts()
    for act in sorted(df["action"].unique(), key=lambda a: _ACTION_ORDER.get(a, 9)):
        if act == "NO_ACTION":
            continue
        block = df[df["action"] == act].head(args.top_n)
        unit_label = "shares" if act == "BUY_STOCK" else "contracts"
        print(f"\n■ {act}  ({counts.get(act, 0)} names)  — '{unit_label}' = suggested size")
        s = block.copy()
        s["stk_px"] = s["stk_px"].round(2)
        s["impl%"] = (s["impl_move"] * 100).round(1)
        s["fcst%"] = (s["forecast_move"] * 100).round(1)
        s["rich"] = s["richness"].round(2)
        s["win%"] = (s["win_prob"] * 100).round(0).astype("Int64")
        s["size_$"] = s["notional"].round(0).astype("Int64")
        # Shares as integer; option contracts to 1dp (a high-priced underlying can need
        # <1 contract at this risk budget → use a spread or skip rather than oversize).
        s[unit_label] = s["units"].round(0).astype("Int64") if act == "BUY_STOCK" else s["units"].round(1)
        s["exp_gain_$"] = s["exp_gain"].round(0).astype("Int64")
        s["max_loss_$"] = s["max_loss"].round(0).astype("Int64")
        s["dte"] = s["days_to_earnings"].astype("Int64")
        s = s[
            [
                "ticker",
                "stk_px",
                "impl%",
                "fcst%",
                "rich",
                "win%",
                "size_$",
                unit_label,
                "exp_gain_$",
                "max_loss_$",
                "dir_action",
                "dte",
            ]
        ]
        print(s.to_string(index=False))

    # ── Recommended BOOK: the actual positions to hold, risk-capped ──
    book = build_book(df, args.capital, args.max_book_risk, args.max_positions, args.max_iv_sell)
    print("\n" + "=" * 78)
    print(
        f"  RECOMMENDED BOOK — best {len(book)} positions by reward/risk, total risk ≤ {args.max_book_risk * 100:.0f}% of capital"
    )
    print("=" * 78)
    if book.empty:
        print("  (no positions pass the filters)")
    else:
        b = book.copy()
        b["win%"] = (b["win_prob"] * 100).round(0).astype("Int64")
        b["size_$"] = b["notional"].round(0).astype("Int64")
        b["units"] = [
            round(u, 0) if a == "BUY_STOCK" else round(u, 1) for u, a in zip(b["units"], b["action"], strict=False)
        ]
        b["exp_gain_$"] = b["exp_gain"].round(0).astype("Int64")
        b["max_loss_$"] = b["max_loss"].round(0).astype("Int64")
        b["RR"] = (b["exp_gain"] / b["max_loss"].clip(lower=1)).round(2)
        print(
            b[["ticker", "action", "stk_px", "win%", "size_$", "units", "exp_gain_$", "max_loss_$", "RR"]].to_string(
                index=False
            )
        )
        tot_gain, tot_risk = book["exp_gain"].sum(), book["max_loss"].sum()
        print("-" * 78)
        print(
            f"  BOOK: {len(book)} positions | expected +${tot_gain:,.0f}/{args.horizon}d "
            f"({tot_gain / args.capital * 100:.2f}% of capital) | avg win {book['win_prob'].mean() * 100:.0f}%"
        )
        print(
            f"  Worst-case correlated loss (all stop at once): −${tot_risk:,.0f} "
            f"({tot_risk / args.capital * 100:.1f}% of capital) | reward/risk {tot_gain / max(tot_risk, 1):.2f}"
        )
        print(
            f"  Notional deployed: ${book['notional'].sum():,.0f}. Premium-sells with ATM IV > {args.max_iv_sell:.0%} excluded."
        )
        book_path = Path(args.output_dir) / f"orats_book_{args.universe}_{summary['latest_date']}.csv"
        book.to_csv(book_path, index=False)
        print(f"  Saved book → {book_path}")

    out_cols = [
        "ticker",
        "action",
        "rationale",
        "stk_px",
        "market_cap",
        "atm_iv_30d",
        "impl_move",
        "forecast_move",
        "richness",
        "win_prob",
        "notional",
        "units",
        "exp_gain",
        "max_loss",
        "richness_pct",
        "dir_action",
        "dir_confidence",
        "dir_score",
        "dir_entry",
        "dir_stop",
        "dir_target",
        "days_to_earnings",
        "total_opt_volume",
    ]
    out_cols = [c for c in out_cols if c in df.columns]
    out_path = Path(args.output_dir) / f"orats_recommendations_{args.universe}_{summary['latest_date']}.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df[out_cols].to_csv(out_path, index=False)
    print(f"\nSaved {len(df)} recommendations → {out_path}")
    print("\nReminder: premium-selling carries short-vol tail risk (this 5-month sample has no vol spike);")
    print("size small, prefer ETF VRP for the cleanest harvest, and never sell premium into earnings.")


if __name__ == "__main__":
    main()
