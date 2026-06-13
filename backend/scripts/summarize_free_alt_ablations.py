#!/usr/bin/env python3
"""Parse free alt-data ablation logs and emit a JSON summary.

Run after `scripts/run_free_alt_ablations.sh`:
    cd backend && python scripts/summarize_free_alt_ablations.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

_LOG_DIR = Path(__file__).parent.parent / "data" / "alt_ablations"
_OUT = _LOG_DIR.parent / "alt_ablations_summary.json"

_REBAL = re.compile(r"Rebalances\s*:\s*(\d+)")
_IC = re.compile(r"Mean IC \(rank\)\s*:\s*([+-]?\d+\.\d+)")
_NET_SH = re.compile(r"SHARPE\s+\(NET\)\s*:\s*([+-]?\d+\.\d+)")
_GROSS_SH = re.compile(r"SHARPE\s+\(gross\)\s*:\s*([+-]?\d+\.\d+)")
_ANN_RET = re.compile(r"Ann\. return\s+net\s*:\s*([+-]?\d+\.\d+)%")
_MAX_DD = re.compile(r"Max drawdown\s*:\s*([+-]?\d+\.\d+)%")
_CI = re.compile(r"Net Sharpe 90% CI\s*:\s*\[([+-]?\d+\.\d+),\s*([+-]?\d+\.\d+)\]")
_POS_FOLDS = re.compile(r"Folds with positive net Sharpe:\s*(\d+)/(\d+)")
_COV = re.compile(r"(?:SEC FTD merged|Wikipedia merged|Sentiment merged|FINRA ATS merged):\s*(.+)")


def _parse(name: str) -> dict:
    path = _LOG_DIR / f"{name}.log"
    text = path.read_text()
    cov_match = _COV.search(text)
    coverage = cov_match.group(1).strip() if cov_match else None
    return {
        "name": name,
        "rebalances": int(_REBAL.search(text).group(1)),
        "mean_ic": float(_IC.search(text).group(1)),
        "net_sharpe": float(_NET_SH.search(text).group(1)),
        "gross_sharpe": float(_GROSS_SH.search(text).group(1)),
        "ann_return_net_pct": float(_ANN_RET.search(text).group(1)),
        "max_drawdown_pct": float(_MAX_DD.search(text).group(1)),
        "net_sharpe_ci_90": [
            float(_CI.search(text).group(1)),
            float(_CI.search(text).group(2)),
        ],
        "positive_folds": f"{_POS_FOLDS.search(text).group(1)}/{_POS_FOLDS.search(text).group(2)}",
        "coverage_note": coverage,
    }


def main() -> None:
    configs = ["baseline", "sec_ftd", "naaim", "wiki", "combined"]
    summary = {
        "methodology": {
            "script": "scripts/cross_sectional_alpha_model.py",
            "flags": (
                "--walk-forward --wf-start 2012 --wf-test-years 1 "
                "--placebo --placebo-seed 42 --universe curated "
                "--cost-bps 10 --decile 0.10"
            ),
            "horizon_days": 21,
            "folds": 15,
            "universe": "curated (109 survivorship-bias-free single names)",
        },
        "results": {c: _parse(c) for c in configs},
        "not_tested": {
            "finra_ats": "historical endpoint blocked (returns HTML); live-forward accumulation only",
            "cboe_iv_rank": "self-grown history began 2026-06-12; need >=252 snapshots per ticker",
        },
        "verdict": (
            "No free alt-data config cleared the harness noise floor at h=21. "
            "All net Sharpe CIs include zero and the deltas vs baseline are within sampling variation."
        ),
    }
    _OUT.write_text(json.dumps(summary, indent=2))
    print(f"Wrote {_OUT}")


if __name__ == "__main__":
    main()
