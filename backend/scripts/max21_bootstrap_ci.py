#!/usr/bin/env python3
"""
Block-bootstrap CI for the MAX-21 low-MAX filter's Sharpe lift.

Reuses the existing Politis-Romano block-bootstrap methodology from
backtest_technicals.monte_carlo() (block size = max(5, round(N^(1/3))),
resampling contiguous blocks to preserve serial autocorrelation) and adds a
PAIRED delta test: for each bootstrap resample of the baseline (unfiltered)
trade timeline, compute both the baseline Sharpe (all trades in the sampled
blocks) and the filtered Sharpe (only the MAX21-surviving subset of those
same blocks), then report the distribution of (filtered - baseline). This
directly tests whether the *lift* is distinguishable from noise, which two
separate marginal CIs cannot answer on their own (they can overlap while the
paired delta is still significant, or vice versa).

Usage:
    python scripts/max21_bootstrap_ci.py \
        --baseline /tmp/trades_baseline_313.csv \
        --filtered /tmp/trades_filtered_264.csv
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd


def trade_sharpe(net_pct: np.ndarray) -> float | None:
    n = len(net_pct)
    if n < 10:
        return None
    std = net_pct.std(ddof=0)
    if std <= 0:
        return None
    return float(net_pct.mean() / std)


def block_bootstrap_ci(net_pct: np.ndarray, n_sims: int = 10000, seed: int = 42) -> tuple[float, float, float]:
    """Return (p5, median, p95) per-trade Sharpe over block-bootstrap resamples."""
    n = len(net_pct)
    block_size = max(5, int(round(n ** (1 / 3))))
    n_blocks_needed = -(-n // block_size)
    rng = np.random.default_rng(seed=seed)
    sims = []
    for _ in range(n_sims):
        starts = rng.integers(0, max(1, n - block_size + 1), size=n_blocks_needed)
        blocks = [net_pct[s : s + block_size] for s in starts]
        sample = np.concatenate(blocks)[:n]
        sh = trade_sharpe(sample)
        sims.append(sh if sh is not None else 0.0)
    return (
        float(np.percentile(sims, 5)),
        float(np.percentile(sims, 50)),
        float(np.percentile(sims, 95)),
    )


def paired_delta_bootstrap(
    baseline: pd.DataFrame, filtered_key: set[tuple], n_sims: int = 10000, seed: int = 42
) -> tuple[float, float, float]:
    """Resample BLOCKS of the baseline (date-ordered) trade timeline; for each
    resample compute baseline Sharpe (all trades in the blocks) and filtered
    Sharpe (only the MAX21-surviving subset of the SAME sampled blocks), then
    return (p5, median, p95) of the delta (filtered - baseline).

    filtered_key: set of (date, ticker) tuples identifying which baseline
    rows survive the MAX21 filter — pairing is preserved because each
    resampled block carries both its full-book and filtered-subset returns.
    """
    n = len(baseline)
    block_size = max(5, int(round(n ** (1 / 3))))
    n_blocks_needed = -(-n // block_size)
    is_filtered = baseline.apply(lambda r: (r["date"], r["ticker"]) in filtered_key, axis=1).values
    net = baseline["net_pct"].values
    rng = np.random.default_rng(seed=seed)
    deltas = []
    for _ in range(n_sims):
        starts = rng.integers(0, max(1, n - block_size + 1), size=n_blocks_needed)
        idx = np.concatenate([np.arange(s, min(s + block_size, n)) for s in starts])[:n]
        sample_net = net[idx]
        sample_mask = is_filtered[idx]
        base_sh = trade_sharpe(sample_net)
        filt_sh = trade_sharpe(sample_net[sample_mask]) if sample_mask.sum() >= 10 else None
        if base_sh is not None and filt_sh is not None:
            deltas.append(filt_sh - base_sh)
    if not deltas:
        return (float("nan"), float("nan"), float("nan"))
    return (
        float(np.percentile(deltas, 5)),
        float(np.percentile(deltas, 50)),
        float(np.percentile(deltas, 95)),
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--filtered", required=True)
    ap.add_argument("--n-sims", type=int, default=10000)
    args = ap.parse_args()

    base = pd.read_csv(args.baseline)
    filt = pd.read_csv(args.filtered)
    base["date"] = pd.to_datetime(base["date"]).dt.strftime("%Y-%m-%d")
    filt["date"] = pd.to_datetime(filt["date"]).dt.strftime("%Y-%m-%d")

    base_net = base["net_pct"].values
    filt_net = filt["net_pct"].values

    print("=" * 72)
    print("MAX21 Filter — Block-Bootstrap Sharpe CI (Politis-Romano)")
    print("=" * 72)
    print(f"\nBaseline (unfiltered): N={len(base)}  point Sharpe={trade_sharpe(base_net):.3f}")
    b5, bmed, b95 = block_bootstrap_ci(base_net, n_sims=args.n_sims)
    print(f"  Block-bootstrap CI (5/50/95 pct): {b5:.3f} / {bmed:.3f} / {b95:.3f}")

    print(f"\nFiltered (MAX21<=q55): N={len(filt)}  point Sharpe={trade_sharpe(filt_net):.3f}")
    f5, fmed, f95 = block_bootstrap_ci(filt_net, n_sims=args.n_sims)
    print(f"  Block-bootstrap CI (5/50/95 pct): {f5:.3f} / {fmed:.3f} / {f95:.3f}")

    filtered_key = set(zip(filt["date"], filt["ticker"]))
    matched = base.apply(lambda r: (r["date"], r["ticker"]) in filtered_key, axis=1).sum()
    print(f"\nPaired match: {matched}/{len(filt)} filtered trades found in baseline by (date,ticker)")

    d5, dmed, d95 = paired_delta_bootstrap(base, filtered_key, n_sims=args.n_sims)
    print("\nPAIRED delta bootstrap (filtered Sharpe - baseline Sharpe, same resampled blocks):")
    print(f"  5th / median / 95th pct: {d5:+.3f} / {dmed:+.3f} / {d95:+.3f}")

    print("\n" + "=" * 72)
    if d5 > 0:
        print(f"VERDICT: Lift is bootstrap-significant at 90% (5th pctile {d5:+.3f} > 0).")
    elif dmed > 0:
        print(
            f"VERDICT: Lift is directionally positive (median {dmed:+.3f}) but NOT significant at 90% (5th pctile {d5:+.3f} <= 0)."
        )
    else:
        print(f"VERDICT: No reliable lift — median delta {dmed:+.3f}.")
    print(f"Baseline marginal CI excludes 0: {b5 > 0}  |  Filtered marginal CI excludes 0: {f5 > 0}")


if __name__ == "__main__":
    main()
