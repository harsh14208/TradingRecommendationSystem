#!/usr/bin/env python3
"""Backfill experiment_registry.jsonl from docs/Stats.md historical sections."""

import json
import re
from pathlib import Path
from typing import Optional


def find_project_root() -> Path:
    """Locate project root by finding docs/Stats.md relative to this script."""
    script_dir = Path(__file__).resolve().parent
    root = script_dir.parent.parent
    if (root / "docs" / "Stats.md").exists():
        return root
    return Path.cwd()


def parse_date(text: str) -> Optional[str]:
    """Extract YYYY-MM-DD from text; return ISO datetime or None."""
    m = re.search(r"(\d{4}-\d{2}-\d{2})", text)
    if m:
        return f"{m.group(1)}T00:00:00"
    return None


def infer_type(header: str, body: str) -> str:
    """Infer experiment_type from header + body text."""
    combined = f"{header} {body}"
    low = combined.lower()
    if "sweep" in low:
        return "parameter_sweep"
    if any(w in low for w in ("ablation", "remove one family", "removing", "families removed", "gate removed")):
        return "gate_ablation"
    if any(
        w in low
        for w in (
            "walk-forward",
            "walk forward",
            "oos validation",
            "oos walk-forward",
            "fixed parameters applied oos",
            "per-window results",
        )
    ):
        return "walk_forward"
    return "backtest_run"


def count_trials(body: str, exp_type: str) -> int:
    """Heuristic: count distinct configurations / rows in tables."""
    lines = body.splitlines()
    tables = []
    current = []
    in_table = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|"):
            in_table = True
            current.append(stripped)
        else:
            if in_table:
                tables.append(current)
                current = []
            in_table = False
    if current:
        tables.append(current)

    best_count = 1
    for table in tables:
        # Count data rows (skip header row and separator row like |---|---|)
        has_separator = any(re.match(r"^\|[-\s:|]+\|$", row) for row in table)
        data_rows = []
        for row in table:
            if re.match(r"^\|[-\s:|]+\|$", row):
                continue
            if re.match(r"^\|[^|]+\|", row):
                data_rows.append(row)
        # If table has a separator, the first data row is the header — remove it
        if has_separator and data_rows:
            data_rows = data_rows[1:]

        if exp_type == "gate_ablation":
            if any(
                "family" in r.lower() or "removed" in r.lower() or "gate removed" in r.lower() for r in data_rows[:2]
            ) or any("gate" in r.lower() for r in data_rows[:2]):
                best_count = max(best_count, len(data_rows))
        elif exp_type == "parameter_sweep":
            if len(data_rows) > 1:
                best_count = max(best_count, len(data_rows))
        elif exp_type == "walk_forward":
            window_rows = [r for r in data_rows if re.search(r"\d{4}[–-](?:\d{4}|pres(?:ent)?)", r)]
            if window_rows:
                best_count = max(best_count, len(window_rows))
            elif len(data_rows) > 1:
                best_count = max(best_count, len(data_rows))
        else:
            # backtest_run: if there's a config/results table with multiple rows, count them
            if len(data_rows) > 1:
                best_count = max(best_count, len(data_rows))

    if best_count == 1:
        m = re.search(
            r"(\d+)\s+(?:configs?|configurations?|trials?|values?|windows?|epochs?|approaches?|families?|experiments?)",
            body,
            re.IGNORECASE,
        )
        if m:
            best_count = int(m.group(1))

    return best_count


def is_report_section_number(header: str) -> bool:
    """Exclude obvious report chapters (1-10, 12-15) from numbered headers."""
    m = re.match(r"^(\d+)[a-z]?\.\s*", header)
    if not m:
        return False
    num = int(m.group(1))
    return num in {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15}


def is_summary_header(header: str) -> bool:
    """Exclude parent-summary headers like '§15 Complete Research Summary'."""
    low = header.lower()
    if re.match(r"^§\d+\s+(complete\s+)?(research\s+)?summary", low):
        return True
    if re.match(r"^§\d+\s+complete\s+leaderboard", low):
        return True
    if re.match(r"^§\d+\s+summary", low):
        return True
    return False


def extract_sections(text: str) -> list[dict]:
    """Parse Stats.md into experiment sections."""
    lines = text.splitlines()
    sections = []

    # Pattern 1: markdown headers with experiment identifiers
    header_re = re.compile(
        r"^(#{1,4}\s+)"
        r"("
        r"§\S+.*|"  # §11a., §QuantEngine, §83
        r"\d+[a-z]?\.\s+.*|"  # 10a. Ablation, 11a. Performance
        r"Inv\d+[a-z]?.*|"  # Inv1, Inv2
        r"QENG-\d+[a-z]?.*|"  # QENG-5a
        r"R\d+[a-z]?\b.*|"  # R1, R7
        r"[A-D]\.\s+.*"  # A. Beta Hedge, B. Portfolio...
        r")$"
    )

    # Pattern 2: blockquote bullets for R1-R7 and QENG items in header block
    bullet_re = re.compile(r"^>\s*•\s*\*\*.*\b(R\d+|QENG-\d+[a-z]?)\b.*\*\*")

    current = None
    for line in lines:
        hm = header_re.match(line)
        bm = bullet_re.match(line)
        if hm:
            header = hm.group(2).strip()
            if is_report_section_number(header) or is_summary_header(header):
                continue  # Skip entirely; don't end current section
            if current:
                sections.append(current)
            current = {
                "header": header,
                "body_lines": [],
            }
        elif bm:
            if current:
                sections.append(current)
            # Extract text from bullet: get the first **...** block
            bold_match = re.search(r"\*\*(.*?)\*\*", line)
            if bold_match:
                header = bold_match.group(1).strip()
            else:
                h = line.strip().lstrip(">").strip()
                h = re.sub(r"^•\s*", "", h)
                header = h.strip()
            current = {
                "header": header,
                "body_lines": [],
            }
        elif current is not None:
            current["body_lines"].append(line)

    if current:
        sections.append(current)

    experiments = []
    for sec in sections:
        header = sec["header"]
        body = "\n".join(sec["body_lines"])
        exp_type = infer_type(header, body)
        trials = count_trials(body, exp_type)
        date = parse_date(header) or parse_date(body) or "2026-01-01T00:00:00"
        hypothesis = header[:200]
        experiments.append(
            {
                "experiment_type": exp_type,
                "hypothesis": hypothesis,
                "number_of_trials": trials,
                "git_sha": None,
                "is_metrics": {},
                "created_at": date,
            }
        )

    return experiments


def main() -> None:
    root = find_project_root()
    stats_path = root / "docs" / "Stats.md"
    jsonl_path = root / "backend" / "data" / "experiment_registry.jsonl"

    if not stats_path.exists():
        print(f"Error: {stats_path} not found")
        return

    text = stats_path.read_text(encoding="utf-8")
    experiments = extract_sections(text)

    # Deduplicate by hypothesis
    existing_hypotheses = set()
    if jsonl_path.exists():
        with jsonl_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    existing_hypotheses.add(rec.get("hypothesis", ""))
                except json.JSONDecodeError:
                    continue

    new_entries = [e for e in experiments if e["hypothesis"] not in existing_hypotheses]

    # Append new entries
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    with jsonl_path.open("a", encoding="utf-8") as f:
        for entry in new_entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    total_trials = sum(e["number_of_trials"] for e in new_entries)
    print(f"Backfilled {len(new_entries)} experiments, total trials: {total_trials}")


if __name__ == "__main__":
    main()
