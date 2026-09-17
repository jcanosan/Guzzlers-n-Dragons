#!/usr/bin/env python3
"""Regenerate evals/RESULTS.md from the latest promptfoo run.

Default prints the markdown table to stdout (safe preview); --write
overwrites evals/RESULTS.md. Meshes with scripts/run_evals.sh --results.
Judge model + date are recorded fresh each render (the :cloud snapshot
rolls silently, see roadmap/evaluation.md).
"""

import argparse
import datetime as dt
import json
from pathlib import Path

RESULTS = Path("evals/RESULTS.md")
LATEST = Path("evals/latest-run.json")

JUDGE = "nemotron-3-super:cloud"


def render(data: dict) -> str:
    stats = data["results"]["stats"]
    tok = stats["tokenUsage"]["assertions"]
    dur = round(stats["durationMs"] / 1000)
    lines = [
        "# Sample eval run",
        "",
        f"Run id: `{data['evalId']}` — pinned "
        f"{dt.datetime.now(dt.UTC).date().isoformat()}. "
        "Regenerate: `scripts/run_evals.sh --results`.",
        "",
        f"Judge: `{JUDGE}` @ 0.1 (see promptfooconfig.yaml defaultTest). "
        "`:cloud` snapshots roll silently — read results together",
        "with this date.",
        "",
        "| Case | Verdict | Failing assertion |",
        "| ---- | ------- | ----------------- |",
    ]
    rows = sorted(
        data["results"]["results"],
        key=lambda r: (r["testCase"].get("description") or "").lower(),
    )
    for row in rows:
        desc = (row["testCase"].get("description") or "?").replace("|", "/")
        comps = (row.get("gradingResult") or {}).get("componentResults", [])
        failed = [a for a in comps if not a["pass"]]
        if not failed:
            lines.append(f"| {desc} | PASS | — |")
        else:
            first = failed[0]["assertion"]
            name = first.get("value") or first.get("type")
            lines.append(f"| {desc} | **FAIL** | `{name}` |")
    lines += [
        "",
        f"**Total: {stats['successes']} passed / {stats['failures']} failed / "
        f"{stats['errors']} errors — {dur}s, judge tokens {tok['total']:,}**",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write RESULTS.md")
    args = parser.parse_args()
    data = json.loads(LATEST.read_text())
    markdown = render(data)
    if args.write:
        RESULTS.write_text(markdown)
        print(f"wrote {RESULTS}")
    else:
        print(markdown, end="")


if __name__ == "__main__":
    main()
