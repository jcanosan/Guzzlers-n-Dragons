# Sample eval run

Run id: `eval-CAR-2026-09-16T08:59:08` — pinned 2026-09-16 (UTC+2 session). Regenerate: `PYTHONPATH=. npx promptfoo eval -c evals/promptfooconfig.yaml`.

Judge: `nemotron-3-super:cloud` @ 0.1 (see promptfooconfig.yaml defaultTest). `:cloud` snapshots roll silently — read results together with this date.

| Case | Verdict | Failing assertion |
| ---- | ------- | ----------------- |
| Anachronism: fantasy feast resisting maize | **FAIL** | `file://banned.py` |
| Anachronism: fantasy grain requesting potato | PASS | — |
| Anachronism: fantasy root recipe holds the tomato line | PASS | — |
| Anachronism: mythological offering declines canned goods | PASS | — |
| Anachronism: mythological stew repels microwave queries | PASS | — |
| Constraint: fifteen-minute mythological dessert | PASS | — |
| Constraint: hard-difficulty fantasy main | PASS | — |
| Constraint: sci-fi feast for eight | PASS | — |
| Constraint: vegetarian emberfruit banquet | PASS | — |
| Fantasy seeded: emberfruit main course | PASS | — |
| Mythological seeded: ambrosia dessert | PASS | — |
| Mythological seeded: dragon-milk porridge | PASS | — |
| Regression: dragon-milk vegetarian porridge | PASS | — |
| Regression: kingroot fantasy main | PASS | — |
| Regression: lotus dream beverage | PASS | — |
| Regression: spice melange keeps producing a dish | PASS | — |
| Sci-fi seeded: nutrient paste breakfast | PASS | — |
| Sci-fi seeded: spice melange main course | PASS | — |

**Total: 17 passed / 1 failed / 0 errors — 364s, judge tokens 26,628**

The single failure is the live anachronism red: the Creator wrote "approximate with high-quality sweet corn" into a fantasy dish and the Critic didn't flag the substitute. Documented in evals/cases.yaml.
