#!/usr/bin/env python3
"""Rigorous alt-data effect attribution for the cross-sectional harness.

Implements the post-audit checklist:
  1. Placebo distribution: 10+ pure-noise seeds at each horizon.
  2. Paired per-fold/rebalance bootstrap of real-feature net returns vs baseline.
  3. Per-fold attribution split by coverage epoch (pre-2019, 2019-2024, post-2024).
  4. Horizon-as-hyperparameter: select horizon on early folds, evaluate on later folds.

Outputs a JSON results file and a concise console summary.  The console summary
is designed to be pasted into docs/LEARNINGS.md as the honest verdict.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

# Allow imports from backend/ when running as script
_HERE = Path(__file__).resolve().parent
_BACKEND = _HERE.parent
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import cross_sectional_alpha_model as csam

_DATA = _BACKEND / "data"


def set_horizon(h: int) -> None:
    """Override the module-level horizon constants before any data is built."""
    csam.HORIZON = h
    csam.PERIODS_PER_YEAR = csam.TRADING_DAYS / h


@dataclass(frozen=True)
class Config:
    """A feature configuration label + the kwargs for build_panel()."""

    name: str
    panel_kwargs: dict[str, Any]


# ---------------------------------------------------------------------------
# Building panels
# ---------------------------------------------------------------------------


def build_panel_for_config(
    config: Config, horizon: int, default_universe: str = "full"
) -> tuple[pd.DataFrame, list[str]]:
    """Build and z-score a panel for a given config/horizon.

    Returns the z-scored panel and the feature column list actually used.
    Config-level kwargs override the default universe when explicitly set.
    """
    set_horizon(horizon)
    panel_kwargs: dict[str, Any] = {"universe_source": default_universe}
    panel_kwargs.update({k: v for k, v in config.panel_kwargs.items() if k != "use_fundamentals"})
    panel = csam.build_panel(**panel_kwargs)
    feature_cols = [c for c in csam.RAW_FEATURE_COLS if c in panel.columns]

    if config.panel_kwargs.get("use_fundamentals"):
        fz = csam._fundamental_factor_panel(sorted(panel["ticker"].unique()))
        panel = panel.merge(fz, on=["date", "ticker"], how="left")
        feature_cols += [c for c in csam.FUND_FACTOR_COLS if c in panel.columns]

    panel = csam.cross_sectional_zscore(panel, feature_cols)
    return panel, feature_cols


def add_placebo(panel: pd.DataFrame, feature_cols: list[str], seed: int) -> tuple[pd.DataFrame, list[str]]:
    """Return a panel copy with 3 pure-noise columns added for ``seed``."""
    rng = np.random.default_rng(seed)
    out = panel.copy()
    new_cols: list[str] = []
    for i in range(3):
        col = f"placebo_{seed}_{i}"
        out[col] = rng.standard_normal(len(out))
        new_cols.append(col)
    return out, feature_cols + new_cols


# ---------------------------------------------------------------------------
# Walk-forward wrapper that keeps per-fold series
# ---------------------------------------------------------------------------


def run_walk_forward(
    panel: pd.DataFrame,
    feature_cols: list[str],
    decile: float,
    cost_bps: float,
    start_year: int,
    test_years: int = 1,
    exit_decile: float | None = None,
) -> dict[str, Any]:
    """Run walk_forward and annotate the result with horizon/config metadata."""
    res = csam.walk_forward(
        panel,
        feature_cols,
        decile=decile,
        cost_bps=cost_bps,
        start_year=start_year,
        test_years=test_years,
        exit_decile=exit_decile,
    )
    # Ensure every fold has a net-return series (used by bootstrap / epoch code).
    for f in res.get("folds", []):
        gross = np.asarray(f["gross"], dtype=float)
        turn = np.asarray(f["turnover"], dtype=float)
        f["net"] = gross - turn * (cost_bps / 1e4)
    return res


# ---------------------------------------------------------------------------
# Placebo distribution
# ---------------------------------------------------------------------------


def placebo_distribution(
    base_panel: pd.DataFrame,
    base_feature_cols: list[str],
    horizon: int,
    seeds: list[int],
    decile: float,
    cost_bps: float,
    start_year: int,
    test_years: int = 1,
    exit_decile: float | None = None,
) -> dict[str, Any]:
    """Run walk-forward for ``seeds`` pure-noise feature sets on the same panel."""
    print(f"\n[placebo h={horizon}] running {len(seeds)} noise seeds ...")
    records = []
    for seed in seeds:
        panel_p, fc_p = add_placebo(base_panel, base_feature_cols, seed)
        panel_p = csam.cross_sectional_zscore(panel_p, fc_p)
        res = run_walk_forward(panel_p, fc_p, decile, cost_bps, start_year, test_years, exit_decile)
        records.append(
            {
                "seed": seed,
                "sharpe_net": res["sharpe_net"],
                "sharpe_gross": res["sharpe_gross"],
                "mean_ic": res["mean_ic"],
                "ann_ret_net": res["ann_ret_net"],
                "ann_vol": res["ann_vol"],
            }
        )
        print(f"  seed {seed:>3}: net Sharpe = {res['sharpe_net']:+.3f}")
    sharpes = np.array([r["sharpe_net"] for r in records])
    return {
        "horizon": horizon,
        "n": len(records),
        "seeds": seeds,
        "sharpe_net_mean": float(np.mean(sharpes)),
        "sharpe_net_std": float(np.std(sharpes, ddof=1)),
        "sharpe_net_min": float(np.min(sharpes)),
        "sharpe_net_max": float(np.max(sharpes)),
        "sharpe_net_median": float(np.median(sharpes)),
        "sharpe_net_q05": float(np.percentile(sharpes, 5)),
        "sharpe_net_q95": float(np.percentile(sharpes, 95)),
        "records": records,
    }


# ---------------------------------------------------------------------------
# Paired per-fold/rebalance bootstrap: real vs baseline
# ---------------------------------------------------------------------------


def _sharpe_from_net(net: np.ndarray) -> float:
    sd = net.std(ddof=1)
    if len(net) <= 2 or sd <= 0:
        return float("nan")
    return float(net.mean() * csam.PERIODS_PER_YEAR / (sd * np.sqrt(csam.PERIODS_PER_YEAR)))


def paired_bootstrap(
    base_folds: list[dict],
    treat_folds: list[dict],
    n_boot: int = 10_000,
    block: int = 4,
    seed: int = 42,
) -> dict[str, Any]:
    """Block-bootstrap paired rebalance returns and report ΔSharpe distribution.

    Folds are paired by chronological order (base/treat must have the same number
    of folds). Within the concatenated paired series we resample contiguous blocks
    to preserve mild serial correlation.
    """
    if len(base_folds) != len(treat_folds):
        raise ValueError("base and treat must have the same number of folds")

    base_net = np.concatenate([np.asarray(f["net"], dtype=float) for f in base_folds])
    treat_net = np.concatenate([np.asarray(f["net"], dtype=float) for f in treat_folds])
    if len(base_net) != len(treat_net):
        # Different horizons produce different numbers of rebals per fold.
        # Fall back to fold-level bootstrap (one draw per fold) which is always paired.
        return _fold_level_paired_bootstrap(base_folds, treat_folds, n_boot, seed)

    diff = treat_net - base_net
    rng = np.random.default_rng(seed)
    n = len(diff)
    if n < block * 3:
        return {"error": "too few rebalance periods for bootstrap"}

    n_blocks = int(np.ceil(n / block))
    delta_sharpes = []
    delta_means = []
    for _ in range(n_boot):
        starts = rng.integers(0, n, size=n_blocks)
        idx = np.concatenate([(np.arange(s, s + block) % n) for s in starts])[:n]
        sample_b = base_net[idx]
        sample_t = treat_net[idx]
        delta_sharpes.append(_sharpe_from_net(sample_t) - _sharpe_from_net(sample_b))
        delta_means.append(float(sample_t.mean() - sample_b.mean()))

    delta_sharpes = np.array(delta_sharpes)
    delta_means = np.array(delta_means)
    obs_sharpe_diff = _sharpe_from_net(treat_net) - _sharpe_from_net(base_net)
    obs_mean_diff = float(treat_net.mean() - base_net.mean())
    null_delta = delta_sharpes - obs_sharpe_diff
    p_two = float(np.mean(np.abs(null_delta) >= np.abs(obs_sharpe_diff)))
    p_one = float(np.mean(delta_sharpes <= 0.0) if obs_sharpe_diff > 0 else np.mean(delta_sharpes >= 0.0))
    return {
        "n_boot": n_boot,
        "block": block,
        "obs_delta_sharpe": float(obs_sharpe_diff),
        "obs_delta_mean_per_period": float(obs_mean_diff),
        "mean_delta_sharpe": float(np.mean(delta_sharpes)),
        "std_delta_sharpe": float(np.std(delta_sharpes, ddof=1)),
        "q05_delta_sharpe": float(np.percentile(delta_sharpes, 5)),
        "q95_delta_sharpe": float(np.percentile(delta_sharpes, 95)),
        "p_value_two_sided": p_two,
        "p_value_one_sided": p_one,
        "mean_delta_per_period": float(np.mean(delta_means)),
        "q05_delta_per_period": float(np.percentile(delta_means, 5)),
        "q95_delta_per_period": float(np.percentile(delta_means, 95)),
    }


def _fold_level_paired_bootstrap(
    base_folds: list[dict],
    treat_folds: list[dict],
    n_boot: int,
    seed: int,
) -> dict[str, Any]:
    """Fallback when horizons produce different rebalance counts: bootstrap folds."""
    rng = np.random.default_rng(seed)
    k = len(base_folds)
    base_sh = np.array([f["sharpe_net"] for f in base_folds])
    treat_sh = np.array([f["sharpe_net"] for f in treat_folds])
    obs = float(np.mean(treat_sh) - np.mean(base_sh))
    diffs = []
    for _ in range(n_boot):
        idx = rng.integers(0, k, size=k)
        diffs.append(float(np.mean(treat_sh[idx]) - np.mean(base_sh[idx])))
    diffs = np.array(diffs)
    null_diff = diffs - obs
    p_two = float(np.mean(np.abs(null_diff) >= np.abs(obs)))
    p_one = float(np.mean(diffs <= 0.0) if obs > 0 else np.mean(diffs >= 0.0))
    return {
        "n_boot": n_boot,
        "level": "fold",
        "obs_delta_sharpe": obs,
        "mean_delta_sharpe": float(np.mean(diffs)),
        "std_delta_sharpe": float(np.std(diffs, ddof=1)),
        "q05_delta_sharpe": float(np.percentile(diffs, 5)),
        "q95_delta_sharpe": float(np.percentile(diffs, 95)),
        "p_value_two_sided": p_two,
        "p_value_one_sided": p_one,
    }


# ---------------------------------------------------------------------------
# Coverage-epoch attribution
# ---------------------------------------------------------------------------


def epoch_sharpe(folds: list[dict], epochs: list[tuple[str, int, int | None]], cost_bps: float) -> dict[str, Any]:
    """Compute net Sharpe per epoch by grouping folds by year.

    ``epochs`` is a list of (label, start_year inclusive, end_year inclusive or None).
    """
    out: dict[str, Any] = {}
    for label, y0, y1 in epochs:
        selected = [f for f in folds if f["fold_year"] >= y0 and (y1 is None or f["fold_year"] <= y1)]
        if not selected:
            out[label] = {"n_folds": 0, "sharpe_net": float("nan"), "n_periods": 0}
            continue
        gross = np.concatenate([np.asarray(f["gross"], dtype=float) for f in selected])
        turn = np.concatenate([np.asarray(f["turnover"], dtype=float) for f in selected])
        stats = csam._stats(gross, turn, cost_bps)
        out[label] = {
            "n_folds": len(selected),
            "n_periods": int(stats["n_periods"]),
            "sharpe_net": stats["sharpe_net"],
            "sharpe_gross": stats["sharpe_gross"],
            "ann_ret_net": stats["ann_ret_net"],
            "ann_vol": stats["ann_vol"],
            "avg_turnover": stats["avg_turnover"],
            "fold_years": [f["fold_year"] for f in selected],
        }
    return out


# Wikipedia: 2015-07 → 2024-12; we approximate as <2019, 2019-2024, >2024.
WIKI_EPOCHS = [("pre_2019", 2012, 2018), ("2019_2024", 2019, 2024), ("post_2024", 2025, None)]

# FINRA SV: 2019-01 → 2024-12.
FINRA_SV_EPOCHS = [("pre_2019", 2012, 2018), ("2019_2024", 2019, 2024), ("post_2024", 2025, None)]

# NAAIM/AAII/UMCSENT cover the whole window, but we still split for comparison.
SENTIMENT_EPOCHS = [("pre_2019", 2012, 2018), ("2019_2024", 2019, 2024), ("post_2024", 2025, None)]


def config_epochs(config_name: str) -> list[tuple[str, int, int | None]]:
    if "finra_sv" in config_name:
        return FINRA_SV_EPOCHS
    if "wiki" in config_name:
        return WIKI_EPOCHS
    if "naaim" in config_name or "sentiment" in config_name:
        return SENTIMENT_EPOCHS
    return WIKI_EPOCHS  # generic split


# ---------------------------------------------------------------------------
# Horizon-as-hyperparameter: select on early folds, evaluate on later folds
# ---------------------------------------------------------------------------


def horizon_selection(
    candidate_horizons: list[int],
    base_config: Config,
    decile: float,
    cost_bps: float,
    start_year: int,
    test_years: int,
    universe: str,
    selection_frac: float = 0.5,
) -> dict[str, Any]:
    """Select horizon on the first ``selection_frac`` folds, then test on the rest.

    This is the honest alternative to sweeping horizons post-hoc and quoting the
    maximum.  Returns the selected horizon and its OOS net Sharpe on the held-out
    folds, plus per-candidate selection-fold Sharpe.
    """
    print("\n[horizon selection] building panels for candidates", candidate_horizons)
    candidate_results: dict[int, dict[str, Any]] = {}
    for h in candidate_horizons:
        panel, fc = build_panel_for_config(base_config, h, default_universe=universe)
        res = run_walk_forward(panel, fc, decile, cost_bps, start_year, test_years)
        candidate_results[h] = res
        print(f"  h={h:>3}: full-sample net Sharpe = {res['sharpe_net']:+.3f}  ({len(res['folds'])} folds)")

    # Split folds by chronology.
    fold_years = [f["fold_year"] for f in candidate_results[candidate_horizons[0]]["folds"]]
    n_folds = len(fold_years)
    split_at = max(1, int(round(n_folds * selection_frac)))
    sel_years = set(fold_years[:split_at])
    test_years_set = set(fold_years[split_at:])

    selection_scores: dict[int, float] = {}
    for h, res in candidate_results.items():
        sel_folds = [f for f in res["folds"] if f["fold_year"] in sel_years]
        if not sel_folds:
            selection_scores[h] = float("-inf")
            continue
        gross = np.concatenate([np.asarray(f["gross"], dtype=float) for f in sel_folds])
        turn = np.concatenate([np.asarray(f["turnover"], dtype=float) for f in sel_folds])
        stats = csam._stats(gross, turn, cost_bps)
        selection_scores[h] = stats["sharpe_net"]
        print(f"  h={h:>3}: selection-fold net Sharpe = {stats['sharpe_net']:+.3f}")

    best_h = max(selection_scores, key=lambda x: selection_scores[x])
    print(f"  selected horizon = {best_h} (selection Sharpe = {selection_scores[best_h]:+.3f})")

    test_folds = [f for f in candidate_results[best_h]["folds"] if f["fold_year"] in test_years_set]
    if not test_folds:
        return {
            "candidate_horizons": candidate_horizons,
            "selection_scores": selection_scores,
            "selected_horizon": best_h,
            "error": "no test folds after selection split",
        }
    gross = np.concatenate([np.asarray(f["gross"], dtype=float) for f in test_folds])
    turn = np.concatenate([np.asarray(f["turnover"], dtype=float) for f in test_folds])
    test_stats = csam._stats(gross, turn, cost_bps)
    print(f"  OOS test-fold net Sharpe (h={best_h}) = {test_stats['sharpe_net']:+.3f}")
    return {
        "candidate_horizons": candidate_horizons,
        "selection_frac": selection_frac,
        "selection_fold_years": sorted(sel_years),
        "test_fold_years": sorted(test_years_set),
        "selection_scores": selection_scores,
        "selected_horizon": best_h,
        "oos_test_sharpe_net": test_stats["sharpe_net"],
        "oos_test_sharpe_gross": test_stats["sharpe_gross"],
        "oos_test_ann_ret_net": test_stats["ann_ret_net"],
        "oos_test_ann_vol": test_stats["ann_vol"],
    }


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser(description="Rigorous alt-data attribution for cross-sectional model")
    ap.add_argument("--horizons", type=int, nargs="+", default=[21, 63], help="horizons to test")
    ap.add_argument("--placebo-seeds", type=int, default=10, help="number of placebo seeds per horizon")
    ap.add_argument("--placebo-seed-start", type=int, default=1, help="first placebo seed")
    ap.add_argument(
        "--configs", type=str, nargs="+", default=["baseline", "wiki", "finra_sv", "naaim"], help="configs to run"
    )
    ap.add_argument(
        "--baseline-config",
        type=str,
        default="baseline",
        help="config to use as the baseline for placebo distribution and paired bootstrap",
    )
    ap.add_argument("--cost-bps", type=float, default=10.0)
    ap.add_argument("--decile", type=float, default=0.10)
    ap.add_argument("--wf-start", type=int, default=2012)
    ap.add_argument("--wf-test-years", type=int, default=1)
    ap.add_argument("--exit-decile", type=float, default=None)
    ap.add_argument("--universe", choices=["full", "curated"], default="full")
    ap.add_argument("--horizon-candidates", type=int, nargs="+", default=[21, 42, 63, 84, 126])
    ap.add_argument("--no-horizon-selection", action="store_true", help="skip horizon-as-hyperparameter step")
    ap.add_argument("--output", type=str, default=str(_DATA / "alt_data_attribution.json"))
    ap.add_argument("--n-boot", type=int, default=10_000)
    ap.add_argument("--block", type=int, default=4)
    args = ap.parse_args()

    # Config definitions.  Each config's baseline feature set is the same price
    # features; only the alt-data merge differs.
    config_map: dict[str, Config] = {
        "baseline": Config("baseline", {}),
        "baseline_curated": Config("baseline_curated", {"universe_source": "curated"}),
        "fundamentals": Config("fundamentals", {"use_fundamentals": True, "universe_source": "curated"}),
        "wiki": Config("wiki", {"use_wiki": True}),
        "finra_sv": Config("finra_sv", {"use_finra_sv": True}),
        "naaim": Config("naaim", {"use_naaim": True}),
        "naaim_wiki": Config("naaim_wiki", {"use_naaim": True, "use_wiki": True}),
    }

    configs = [config_map[c] for c in args.configs if c in config_map]
    if not configs:
        raise SystemExit("No valid configs selected")

    results: dict[str, Any] = {
        "meta": {
            "horizons": args.horizons,
            "configs": [c.name for c in configs],
            "cost_bps": args.cost_bps,
            "decile": args.decile,
            "wf_start": args.wf_start,
            "wf_test_years": args.wf_test_years,
            "universe": args.universe,
        }
    }

    # ------------------------------------------------------------------
    # 1) Real configs: baseline + alt-data at each horizon.
    # ------------------------------------------------------------------
    real_results: dict[str, dict[str, Any]] = {}
    for h in args.horizons:
        print(f"\n{'=' * 64}\nHORIZON = {h}\n{'=' * 64}")
        for cfg in configs:
            print(f"\n[config {cfg.name} h={h}]")
            panel, fc = build_panel_for_config(cfg, h, default_universe=args.universe)
            res = run_walk_forward(
                panel, fc, args.decile, args.cost_bps, args.wf_start, args.wf_test_years, args.exit_decile
            )
            print(f"  full-sample net Sharpe = {res['sharpe_net']:+.3f}  ({len(res['folds'])} folds)")
            key = f"{cfg.name}_h{h}"
            real_results[key] = {
                "config": cfg.name,
                "horizon": h,
                "sharpe_net": res["sharpe_net"],
                "sharpe_gross": res["sharpe_gross"],
                "mean_ic": res["mean_ic"],
                "ann_ret_net": res["ann_ret_net"],
                "ann_vol": res["ann_vol"],
                "sharpe_ci": res["sharpe_ci"],
                "folds": res["folds"],
            }
            # Epoch attribution for alt-data configs.
            if cfg.name not in (args.baseline_config, "baseline", "baseline_curated"):
                real_results[key]["epoch_sharpe"] = epoch_sharpe(res["folds"], config_epochs(cfg.name), args.cost_bps)

    results["real_configs"] = real_results

    # ------------------------------------------------------------------
    # 2) Placebo distribution at each horizon.
    # ------------------------------------------------------------------
    placebo_results: dict[int, dict[str, Any]] = {}
    for h in args.horizons:
        baseline_cfg = config_map[args.baseline_config]
        panel, fc = build_panel_for_config(baseline_cfg, h, default_universe=args.universe)
        seeds = list(range(args.placebo_seed_start, args.placebo_seed_start + args.placebo_seeds))
        placebo_results[h] = placebo_distribution(
            panel,
            fc,
            h,
            seeds,
            args.decile,
            args.cost_bps,
            args.wf_start,
            args.wf_test_years,
            args.exit_decile,
        )
    results["placebo"] = placebo_results

    # ------------------------------------------------------------------
    # 3) Paired bootstrap: each real config vs baseline at each horizon.
    # ------------------------------------------------------------------
    bootstrap_results: dict[str, dict[str, Any]] = {}
    for h in args.horizons:
        base_key = f"{args.baseline_config}_h{h}"
        if base_key not in real_results:
            raise SystemExit(f"Baseline config '{args.baseline_config}' must be included in --configs")
        base_folds = real_results[base_key]["folds"]
        for cfg in configs:
            if cfg.name == args.baseline_config:
                continue
            key = f"{cfg.name}_vs_baseline_h{h}"
            treat_folds = real_results[f"{cfg.name}_h{h}"]["folds"]
            print(f"\n[bootstrap {key}]")
            bs = paired_bootstrap(base_folds, treat_folds, n_boot=args.n_boot, block=args.block)
            bootstrap_results[key] = bs
            print(f"  observed ΔSharpe = {bs['obs_delta_sharpe']:+.3f}")
            print(f"  90% CI           = [{bs['q05_delta_sharpe']:+.3f}, {bs['q95_delta_sharpe']:+.3f}]")
            print(f"  two-sided p      = {bs['p_value_two_sided']:.3f}")
    results["paired_bootstrap"] = bootstrap_results

    # ------------------------------------------------------------------
    # 4) Horizon-as-hyperparameter (baseline only).
    # ------------------------------------------------------------------
    if not args.no_horizon_selection:
        print(f"\n{'=' * 64}\nHORIZON AS HYPERPARAMETER (baseline)\n{'=' * 64}")
        results["horizon_selection"] = horizon_selection(
            args.horizon_candidates,
            config_map["baseline"],
            args.decile,
            args.cost_bps,
            args.wf_start,
            args.wf_test_years,
            args.universe,
        )

    # ------------------------------------------------------------------
    # Persist and summarize
    # ------------------------------------------------------------------
    # Drop numpy arrays before JSON serialization; fold series are already arrays.
    def _clean(o: Any) -> Any:
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, (np.floating, np.integer)):
            return float(o) if isinstance(o, np.floating) else int(o)
        if isinstance(o, dict):
            return {k: _clean(v) for k, v in o.items()}
        if isinstance(o, list):
            return [_clean(v) for v in o]
        if isinstance(o, tuple):
            return [_clean(v) for v in o]
        return o

    clean_results = _clean(results)
    out_path = Path(args.output)
    out_path.write_text(json.dumps(clean_results, indent=2, default=str))
    print(f"\nFull results written to: {out_path}")

    # Console summary.
    print("\n" + "=" * 64)
    print("ALT-DATA ATTRIBUTION SUMMARY")
    print("=" * 64)
    for h in args.horizons:
        p = placebo_results[h]
        print(
            f"\nhorizon={h}  placebo band: mean={p['sharpe_net_mean']:+.3f}  "
            f"5%-95%=[{p['sharpe_net_q05']:+.3f},{p['sharpe_net_q95']:+.3f}]  "
            f"min/max=[{p['sharpe_net_min']:+.3f},{p['sharpe_net_max']:+.3f}]"
        )
        for cfg in configs:
            key = f"{cfg.name}_h{h}"
            r = real_results[key]
            marker = ""
            if cfg.name != "baseline":
                if r["sharpe_net"] > p["sharpe_net_max"]:
                    marker = "  [above placebo band]"
                elif r["sharpe_net"] < p["sharpe_net_min"]:
                    marker = "  [below placebo band]"
                else:
                    marker = "  [inside placebo band]"
            print(
                f"  {cfg.name:<12} net Sh={r['sharpe_net']:+.3f}  gross Sh={r['sharpe_gross']:+.3f}  "
                f"IC={r['mean_ic']:+.4f}{marker}"
            )
    print("\nPaired bootstrap ΔSharpe (real vs baseline):")
    for key, bs in bootstrap_results.items():
        print(
            f"  {key:<28} ΔSh={bs['obs_delta_sharpe']:+.3f}  "
            f"90%CI=[{bs['q05_delta_sharpe']:+.3f},{bs['q95_delta_sharpe']:+.3f}]  "
            f"p={bs['p_value_two_sided']:.3f}"
        )
    if "horizon_selection" in results:
        hs = results["horizon_selection"]
        print(
            f"\nHorizon-as-hyperparameter: selected h={hs['selected_horizon']}  "
            f"OOS test-fold net Sharpe = {hs['oos_test_sharpe_net']:+.3f}"
        )
    print("=" * 64)


if __name__ == "__main__":
    main()
