"""§93d: Live-vs-IS gap decomposition."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sqlalchemy import select

sys.path.insert(0, str(Path(__file__).parent.parent))

from database import AsyncSessionLocal
from models import Signal, BrokerOrder


def _to_et(dt: pd.Series) -> pd.Series:
    """Convert naive UTC timestamps to ET hour (handles DST via ZoneInfo)."""
    try:
        from zoneinfo import ZoneInfo
        return dt.dt.tz_localize("UTC").dt.tz_convert("America/New_York")
    except Exception:
        # Fallback: subtract 4h (EDT) or 5h (EST) based on date heuristic
        def _offset(d: pd.Timestamp) -> pd.Timedelta:
            import datetime as _dt
            year = d.year
            dst_start = _dt.date(year, 3, 8 + (6 - _dt.date(year, 3, 1).weekday()) % 7)
            dst_end = _dt.date(year, 11, 1 + (6 - _dt.date(year, 11, 1).weekday()) % 7)
            if dst_start <= d.date() < dst_end:
                return pd.Timedelta(hours=4)
            return pd.Timedelta(hours=5)
        # Vectorized fallback
        offsets = dt.apply(lambda x: _offset(pd.to_datetime(x)) if pd.notna(x) else pd.Timedelta(0))
        return dt - offsets


async def main():
    async with AsyncSessionLocal() as db:
        res = await db.execute(
            select(
                Signal.ticker, Signal.created_at, Signal.action,
                Signal.confidence, Signal.outcome_pct, Signal.outcome_14d,
                Signal.extra_data, Signal.sent_at, Signal.sector_etf,
                Signal.session,
            ).where(Signal.outcome_pct != None, Signal.action.in_(["BUY", "SELL"]))
        )
        signals = pd.DataFrame(res.all(), columns=[
            "ticker", "created_at", "action", "confidence",
            "outcome_pct", "outcome_14d", "extra_data", "sent_at", "sector_etf",
            "session",
        ])
        signals = signals.copy()
        signals["created_at"] = pd.to_datetime(signals["created_at"])
        signals["sent_at"] = pd.to_datetime(signals["sent_at"])
        signals["vix"] = signals["extra_data"].apply(
            lambda x: x.get("vix") if isinstance(x, dict) else None
        )

        res2 = await db.execute(
            select(
                BrokerOrder.symbol, BrokerOrder.created_at,
                BrokerOrder.avg_fill_price, BrokerOrder.arrival_price, BrokerOrder.spread,
            ).where(BrokerOrder.avg_fill_price != None)
        )
        fills = pd.DataFrame(res2.all(), columns=[
            "symbol", "filled_at", "avg_fill_price", "arrival_price", "spread"
        ])
        fills = fills.copy()
        fills["filled_at"] = pd.to_datetime(fills["filled_at"])

    print("=" * 60)
    print("§93d: Live-vs-IS Gap Decomposition")
    print("=" * 60)

    # ── Compute ET hour BEFORE cohort split ─────────────────────────────────
    # For reliable cohort (May+), created_at is UTC → convert to ET.
    # For unreliable cohort (Apr), assume stored hour already reflects ET.
    signals = signals.copy()
    signals["hour_et"] = np.nan
    may_cutoff = pd.Timestamp("2026-05-01", tz=None)
    reliable_mask = signals["created_at"] >= may_cutoff
    unreliable_mask = signals["created_at"] < may_cutoff
    if reliable_mask.any():
        reliable_et = _to_et(signals.loc[reliable_mask, "created_at"])
        signals.loc[reliable_mask, "hour_et"] = reliable_et.dt.hour
    if unreliable_mask.any():
        signals.loc[unreliable_mask, "hour_et"] = signals.loc[unreliable_mask, "created_at"].dt.hour

    # ── Cohort split ────────────────────────────────────────────────────────
    # PostgreSQL is UTC since June 2026. Pre-May signals may reflect a previous
    # deployment's timezone conventions. We split for latency reliability.
    reliable = signals[reliable_mask].copy()
    unreliable = signals[unreliable_mask].copy()

    print("\n## 0. Data Quality & Timestamp Notes\n")
    print(f"Live resolved signals: {len(signals)}")
    print(f"  Reliable cohort (May+):   {len(reliable)}")
    print(f"  Unreliable cohort (Apr):  {len(unreliable)}  (pre-date current codebase)")
    print(f"Signals with extra_data: {signals['extra_data'].notna().sum()}")
    print(f"Signals with VIX in extra_data: {signals['vix'].notna().sum()}/{len(signals)}")
    if signals["vix"].notna().sum() == 0:
        print(
            "> VIX missing from all resolved signals — these rows pre-date the 2026-06-10"
        )
        print(
            "  scanner fix that populates extra_data. New signals going forward WILL"
        )
        print("  have VIX. This is a data-history issue, not a live bug.")

    print("\n## 1. Regime Mismatch (VIX distribution)\n")
    vix_valid = signals.dropna(subset=["vix"]).copy()
    if len(vix_valid) > 0:
        vix_valid["vix_bucket"] = pd.cut(
            vix_valid["vix"],
            bins=[0, 15, 20, 25, 30, 35, 100],
            labels=["<15", "15-20", "20-25", "25-30", "30-35", ">35"],
        )
        vix_dist = vix_valid.groupby("vix_bucket", observed=False).agg(
            n=("outcome_pct", "count"),
            wr=("outcome_pct", lambda x: (x > 0).mean() * 100),
            avg=("outcome_pct", "mean"),
        )
        print(vix_dist.round(2).to_string())
    else:
        print("No VIX data available (pre-fix signals).")

    print("\n> Backtest regime split: 100% of trades in VIX 20-30")
    print("> Live VIX distribution will be available once post-fix signals resolve.")

    print("\n## 2. Delivery Latency\n")
    reliable["latency_sec"] = (reliable["sent_at"] - reliable["created_at"]).dt.total_seconds()
    if len(reliable) > 0 and reliable["sent_at"].notna().sum() > 0:
        lat = reliable["latency_sec"].dropna()
        print(f"Reliable cohort (May+) latency:")
        print(f"  Mean:   {lat.mean():.1f}s")
        print(f"  Median: {lat.median():.1f}s")
        print(f"  P95:    {lat.quantile(0.95):.1f}s")
        late = lat[lat > 300]
        if len(late) > 0:
            print(f"  > 5 min: {len(late)} ({len(late)/len(lat)*100:.1f}%)")
    else:
        print("No reliable latency data.")

    if len(unreliable) > 0:
        print(f"\n⚠️  {len(unreliable)} April signals have unreliable latency")
        print("   (created by previous codebase with different timezone handling)")

    print("\n## 3. Spread at Fill\n")
    if fills.empty:
        print("No fill data available.")
    else:
        print(f"Filled orders: {len(fills)}")
        spreads = fills["spread"].dropna()
        if len(spreads) > 0:
            print(f"Mean spread: {spreads.mean():.3f}%")
            print(f"Median spread: {spreads.median():.3f}%")
        fills["slippage_bps"] = (fills["avg_fill_price"] - fills["arrival_price"]) / fills["arrival_price"] * 10000
        slip = fills["slippage_bps"].dropna()
        if len(slip) > 0:
            print(f"Mean slippage: {slip.mean():.1f} bps")
            print(f"Median slippage: {slip.median():.1f} bps")

    print("\n## 4. Session Timing\n")
    hour_stats = signals.groupby("hour_et").agg(
        n=("outcome_pct", "count"),
        wr=("outcome_pct", lambda x: (x > 0).mean() * 100),
        avg=("outcome_pct", "mean"),
        conf_mean=("confidence", "mean"),
    ).sort_values("wr", ascending=False)
    print(hour_stats.round(2).to_string())

    # Statistical test: worst vs best hours
    print("\n### Session timing statistical tests\n")
    # Compare catastrophic hours (11, 12) against all other hours
    cata_hours = [11, 12]
    cata_sigs = signals[signals["hour_et"].isin(cata_hours)]
    other_sigs = signals[~signals["hour_et"].isin(cata_hours)]
    cata_returns = cata_sigs["outcome_pct"].dropna()
    other_returns = other_sigs["outcome_pct"].dropna()
    if len(cata_returns) >= 10 and len(other_returns) >= 10:
        t_stat, p_val = stats.ttest_ind(cata_returns, other_returns, equal_var=False)
        print(f"Catastrophic (11–12h ET): N={len(cata_returns)}, WR={(cata_returns > 0).mean()*100:.1f}%, avg={cata_returns.mean():+.2f}%")
        print(f"All other hours:          N={len(other_returns)}, WR={(other_returns > 0).mean()*100:.1f}%, avg={other_returns.mean():+.2f}%")
        sig_str = "✅ significant" if p_val < 0.05 else "— not significant"
        print(f"Welch t-test: t={t_stat:.2f}, p={p_val:.3f} {sig_str}")

    catastrophic = hour_stats[(hour_stats["wr"] < 30) & (hour_stats["n"] >= 10)]
    if len(catastrophic) > 0:
        print(f"\n🚨 Catastrophic hours (WR < 30%, N ≥ 10):")
        for h, row in catastrophic.iterrows():
            print(f"   Hour {h:02.0f}: WR={row['wr']:.1f}% (N={row['n']:.0f}), avg={row['avg']:+.2f}%, conf={row['conf_mean']:.1f}")
        # Show cohort breakdown for catastrophic hours
        print(f"\n   Cohort breakdown for catastrophic hours:")
        for h in catastrophic.index:
            apr_n = len(unreliable[unreliable["hour_et"] == h]) if len(unreliable) > 0 else 0
            apr_wr = (unreliable[unreliable["hour_et"] == h]["outcome_pct"] > 0).mean() * 100 if apr_n > 0 else 0
            may_n = len(reliable[reliable["hour_et"] == h]) if len(reliable) > 0 else 0
            may_wr = (reliable[reliable["hour_et"] == h]["outcome_pct"] > 0).mean() * 100 if may_n > 0 else 0
            print(f"     Hour {h:02.0f}: Apr N={apr_n} WR={apr_wr:.1f}% | May+ N={may_n} WR={may_wr:.1f}%")

    print("\n## 5. Session Type (premarket / regular / afterhours)\n")
    if signals["session"].notna().any():
        session_stats = signals.groupby("session").agg(
            n=("outcome_pct", "count"),
            wr=("outcome_pct", lambda x: (x > 0).mean() * 100),
            avg=("outcome_pct", "mean"),
        ).sort_values("wr", ascending=False)
        print(session_stats.round(2).to_string())
    else:
        print("No session data available (column may be NULL for pre-fix signals).")

    print("\n## 6. Per-Sector Live Performance\n")
    sector_stats = signals.groupby("sector_etf").agg(
        n=("outcome_pct", "count"),
        wr=("outcome_pct", lambda x: (x > 0).mean() * 100),
        avg=("outcome_pct", "mean"),
    ).sort_values("wr", ascending=False)
    print(sector_stats.round(2).to_string())

    print("\n## 7. Confidence Analysis for Catastrophic Hours\n")
    if len(catastrophic) > 0:
        for h in catastrophic.index:
            hour_sigs = signals[signals["hour_et"] == h]
            low_conf = hour_sigs[hour_sigs["confidence"] < 60]
            high_conf = hour_sigs[hour_sigs["confidence"] >= 60]
            print(f"\nHour {h:02.0f} ET:")
            if len(low_conf) > 0:
                lc_wr = (low_conf["outcome_pct"] > 0).mean() * 100
                print(f"  Low confidence (<60):  N={len(low_conf)}, WR={lc_wr:.1f}%, avg={low_conf['outcome_pct'].mean():+.2f}%")
            if len(high_conf) > 0:
                hc_wr = (high_conf["outcome_pct"] > 0).mean() * 100
                print(f"  High confidence (≥60): N={len(high_conf)}, WR={hc_wr:.1f}%, avg={high_conf['outcome_pct'].mean():+.2f}%")

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    live_wr = (signals["outcome_pct"] > 0).mean() * 100
    live_avg = signals["outcome_pct"].mean()
    print(f"Live WR: {live_wr:.1f}%  |  Live Avg: {live_avg:+.2f}%")
    print(f"IS WR:   69.1%  |  IS Avg:   +0.80%")
    print(f"Gap:     {69.1 - live_wr:.1f}pp  |  Avg gap: {0.80 - live_avg:+.2f}%")

    vix_20_30 = signals[(signals["vix"] >= 20) & (signals["vix"] <= 30)]
    if len(vix_20_30) > 0:
        regime_wr = (vix_20_30["outcome_pct"] > 0).mean() * 100
        print(f"\nLive WR in VIX 20-30 (backtest regime): {regime_wr:.1f}% (N={len(vix_20_30)})")
    outside = signals[(signals["vix"] < 20) | (signals["vix"] > 30)]
    if len(outside) > 0:
        outside_wr = (outside["outcome_pct"] > 0).mean() * 100
        print(f"Live WR outside VIX 20-30: {outside_wr:.1f}% (N={len(outside)})")

    print("\n" + "=" * 60)
    print("Recommendations")
    print("=" * 60)
    recs = []
    if len(catastrophic) > 0:
        hours = ", ".join(f"{h:02.0f}:00" for h in catastrophic.index)
        recs.append(f"• Consider suppressing signals during catastrophic hours: {hours} ET")
        recs.append("  (Hour 11–12 = midday; possible midday liquidity/microstructure effect)")
    if signals["vix"].notna().sum() == 0:
        recs.append("• VIX not available in historical signals — wait for post-fix signals to resolve")
    if len(unreliable) > 0:
        recs.append(f"• {len(unreliable)} April signals have unreliable timestamps (pre-current codebase)")
    if len(recs) == 0:
        recs.append("• No immediate action items from this decomposition")
    for r in recs:
        print(r)


if __name__ == "__main__":
    asyncio.run(main())
