#!/usr/bin/env bash
# Run free alt-data ablations vs placebo in the cross-sectional harness.
# Outputs are written to data/alt_ablations/{name}.log.
# Note: FINRA ATS historical backfill is blocked by the endpoint (returns HTML),
# and CBOE IV-rank history is live-forward only (<1 day accrued as of 2026-06-12),
# so neither is included here.
set -euo pipefail
cd "$(dirname "$0")/.."
source ../.venv311/bin/activate

OUTDIR="data/alt_ablations"
mkdir -p "$OUTDIR"

COMMON="--walk-forward --wf-start 2012 --wf-test-years 1 --placebo --placebo-seed 42 --universe curated --cost-bps 10 --decile 0.10"

run() {
  local name=$1
  shift
  echo "=== $(date -u +%Y-%m-%dT%H:%M:%SZ)  $name ==="
  python scripts/cross_sectional_alpha_model.py $COMMON "$@" 2>&1 | tee "$OUTDIR/${name}.log"
}

run baseline
run sec_ftd --sec-ftd
run naaim --naaim
run wiki --wiki
run combined --sec-ftd --naaim --wiki

echo "=== Done ==="
ls -l "$OUTDIR"
