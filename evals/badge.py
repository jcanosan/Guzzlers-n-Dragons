"""Render the eval pass-rate badge JSON for shields.io endpoint badges.

Scans for promptfoo's `output-*.json` (the promptfoo-action writes one per
run) and writes `.github/badges/eval.json`. Exits 1 when no output file
exists so the badge step fails loudly but the eval itself still reports.
"""

import glob
import json
import os

ROOT = __file__.rsplit("/", 2)[0] if "/" in __file__ else os.getcwd()


def main() -> None:
    files = glob.glob("output-*.json") or glob.glob("**/output-*.json")
    if not files:
        raise SystemExit("no eval output json found")
    latest = max(files, key=os.path.getmtime)
    stats = json.load(open(latest))["results"]["stats"]
    total = stats["successes"] + stats["failures"] + stats["errors"]
    pct = stats["successes"] / total if total else 0
    color = "brightgreen" if pct == 1 else "gold" if pct >= 0.95 else "red"
    badge = {
        "schemaVersion": 1,
        "label": "agent evals",
        "message": f"{stats['successes']}/{total}",
        "color": color,
    }
    os.makedirs(".github/badges", exist_ok=True)
    with open(".github/badges/eval.json", "w") as fh:
        json.dump(badge, fh)
    print(f"badge updated: {badge['message']} ({pct:.0%}) from {latest}")


if __name__ == "__main__":
    main()
