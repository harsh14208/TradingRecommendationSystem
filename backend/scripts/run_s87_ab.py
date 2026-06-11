#!/usr/bin/env python3
"""§87 A/B backtest wrapper — baseline vs consec-score-sizing with --portfolio."""

import subprocess
import sys
import re
import json
from datetime import datetime, timezone

SCRIPT = "scripts/backtest_technicals.py"
LOG = "/tmp/s87_ab_full.log"
RESULTS = "/tmp/s87_ab_results.json"


def run_variant(label: str, extra_args: list[str]) -> dict:
    print(f"\n{'=' * 60}")
    print(f"RUNNING: {label}")
    print(f"{'=' * 60}\n", flush=True)

    cmd = [sys.executable, "-u", SCRIPT, "--sequential", "--portfolio"] + extra_args
    with open(LOG, "a") as f:
        f.write(f"\n{'=' * 60}\n{label}\n{'=' * 60}\n")
        f.flush()
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        for line in proc.stdout:
            print(line, end="", flush=True)
            f.write(line)
            f.flush()
        proc.wait()

    return extract_metrics(LOG, label)


def extract_metrics(log_path: str, label: str) -> dict:
    with open(log_path) as f:
        content = f.read()

    section_marker = f"{'=' * 60}\n{label}\n{'=' * 60}"
    idx = content.rfind(section_marker)
    if idx == -1:
        return {"error": f"section {label} not found"}

    section = content[idx:]
    next_variant = section.find("\n" + "=" * 60 + "\n", 1)
    if next_variant != -1:
        section = section[:next_variant]

    metrics: dict = {"label": label}

    # ── Per-trade summary (§1) ──
    m = re.search(r"\|\s+Total Trades\s+\|\s+(\d+)\s+\|", section)
    if m:
        metrics["total_trades"] = int(m.group(1))
    m = re.search(r"\|\s+Win Rate\s+\|\s+([\d.]+)%\s+\|", section)
    if m:
        metrics["win_rate"] = float(m.group(1))
    m = re.search(r"\|\s+Avg Return / Trade\s+\|\s+([+-]?[\d.]+)%\s+\|", section)
    if m:
        metrics["avg_return"] = float(m.group(1))
    m = re.search(r"\|\s+Sharpe Ratio\s+\|\s+([\d.]+|—)\s+\|", section)
    if m and m.group(1) != "—":
        metrics["sharpe"] = float(m.group(1))
    m = re.search(r"\|\s+Max Drawdown\s+\|\s+-([\d.]+)%\s+\|", section)
    if m:
        metrics["max_dd"] = float(m.group(1))
    m = re.search(r"\|\s+Profit Factor\s+\|\s+([\d.]+)×\s+\|", section)
    if m:
        metrics["profit_factor"] = float(m.group(1))
    m = re.search(r"\|\s+Avg Win\s+\|\s+([+-]?[\d.]+)%\s+\|", section)
    if m:
        metrics["avg_win"] = float(m.group(1))
    m = re.search(r"\|\s+Avg Loss\s+\|\s+([+-]?[\d.]+)%\s+\|", section)
    if m:
        metrics["avg_loss"] = float(m.group(1))

    # ── Monte Carlo P5/P95 ──
    m = re.search(
        r"Monte Carlo Sharpe \(block bootstrap N=\d+, block=\d+, 5th/95th pct\):\s+([-\d.]+)\s+/\s+([-\d.]+)",
        section,
    )
    if m:
        metrics["mc_p5"] = float(m.group(1))
        metrics["mc_p95"] = float(m.group(2))

    # ── BUY breakdown (§2) ──
    m = re.search(
        r"\*\*BUY\*\*\s+\|\s+(\d+)\s+\|\s+([\d.]+)%\s+\|\s+([+-]?[\d.]+)%\s+\|\s+([\d.]+)×\s+\|\s+([\d.]+|—)",
        section,
    )
    if m:
        metrics["buy_n"] = int(m.group(1))
        metrics["buy_wr"] = float(m.group(2))
        if m.group(5) != "—":
            metrics["buy_sharpe"] = float(m.group(5))

    # ── Portfolio simulation (§QuantEngine) ──
    m = re.search(r"\|\s+CAGR\s+\|\s+([+-]?[\d.]+)%\s+\|", section)
    if m:
        metrics["portfolio_cagr"] = float(m.group(1))
    m = re.search(r"\|\s+Annualized Sharpe\s+\|\s+([\d.]+|—)\s+\|", section)
    if m and m.group(1) != "—":
        metrics["portfolio_ann_sharpe"] = float(m.group(1))
    m = re.search(r"\|\s+Portfolio Max DD\s+\|\s+-([\d.]+)%\s+\|", section)
    if m:
        metrics["portfolio_max_dd"] = float(m.group(1))
    m = re.search(r"\|\s+Skipped \(slots full\)\s+\|\s+(\d+)\s+\|", section)
    if m:
        metrics["portfolio_skipped"] = int(m.group(1))

    return metrics


def main():
    open(LOG, "w").close()

    baseline = run_variant("BASELINE (canon, §94 default)", [])
    variant = run_variant("§87 CONSEC-SCORE-SIZING", ["--consec-score-sizing"])

    def delta(key):
        bv = baseline.get(key)
        vv = variant.get(key)
        if bv is not None and vv is not None:
            return round(vv - bv, 4)
        return None

    comparison = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "baseline": baseline,
        "variant": variant,
        "delta": {
            "total_trades": delta("total_trades"),
            "win_rate": delta("win_rate"),
            "avg_return": delta("avg_return"),
            "sharpe": delta("sharpe"),
            "max_dd": delta("max_dd"),
            "profit_factor": delta("profit_factor"),
            "mc_p5": delta("mc_p5"),
            "portfolio_cagr": delta("portfolio_cagr"),
            "portfolio_ann_sharpe": delta("portfolio_ann_sharpe"),
            "portfolio_max_dd": delta("portfolio_max_dd"),
            "portfolio_skipped": delta("portfolio_skipped"),
        },
    }

    with open(RESULTS, "w") as f:
        json.dump(comparison, f, indent=2)

    print(f"\n{'=' * 60}")
    print("§87 A/B COMPLETE")
    print(f"{'=' * 60}")
    print(json.dumps(comparison, indent=2))
    print(f"\nFull log: {LOG}")
    print(f"Results: {RESULTS}")


if __name__ == "__main__":
    main()
