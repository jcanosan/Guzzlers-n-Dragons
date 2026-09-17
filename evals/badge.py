"""Render the eval pass-rate badge JSON for shields.io endpoint badges.

Reads the deterministic results file `evals/latest-run.json` (written by
promptfoo via `outputPath` in promptfooconfig.yaml) and writes
`.github/badges/eval.json`. Falls back to promptfoo-action's
`output-*.json` for older runs. Exits 1 when nothing is found so the
badge step fails loudly while the eval step itself already reported.
"""

import glob
import json
import os


def main() -> None:
    files = (
        ["evals/latest-run.json"]
        if os.path.exists("evals/latest-run.json")
        else glob.glob("output-*.json")
    )
    if not files:
        raise SystemExit("no eval output found")
    latest = files[0]
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
