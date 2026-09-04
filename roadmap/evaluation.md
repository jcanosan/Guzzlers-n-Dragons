# Agent Evaluation Plan

Goal: demonstrate eval-driven development as a portfolio signal. A golden dataset of
real failure modes + a Promptfoo harness that measures whether the Planner → Creator →
Critic pipeline actually catches what it claims to. Manual run only — no CI gate yet.

## Key technical insight

- The eval provider wraps the **same** `agent_graph.astream` call used by `scripts/demo.py`,
  so evals exercise the real compiled graph, not a mock.
- Highest-value cases test **absence**, not just presence: an anachronism the Critic must
  reject (e.g. potatoes in a fantasy feast) asserts the ingredient is *not* in the final
  recipe and the report flags it.
- The interesting trajectory signal (did the Critic reject correctly, how many iterations)
  is captured cheaply with deterministic assertions on the final state — no tool-path tracing
  needed for this fixed loop.
- External APIs (USDA/TheMealDB/OFF) run live in eval mode: simplest, shows the real
  pipeline. Accepted tradeoff: flaky APIs cause occasional false fails.

## Tooling

- **Promptfoo** via `npx` (no repo dependencies; Node present in dev env). Free, local,
  official LangGraph integration, first-class Ollama support (provider, judge, embeddings).
  Python provider pattern keeps eval logic in Python.
- **Judge model**: `ollama:chat:gemma4:31b-cloud` at temperature 0.1 for `llm-rubric`
  assertions. Same family as the generator → accept circularity or use a stronger judge
  later; document the choice.

## Phases

### Phase 1 — Scaffold
- `evals/provider.py`: Python provider with `call_api(prompt, options, context)`; rebuilds
  `AlchemyRequest` from vars, `init_db()` + `vector_store.init()`, streams the graph, returns
  recipe + report + iteration count.
- `evals/promptfooconfig.yaml`: passthrough prompt, `pythonPath` → `.venv/bin/python`,
  `PYTHONPATH=.`.
- `evals/cases.yaml`: 3–5 smoke cases (one per theme).

Acceptance: `PYTHONPATH=. npx promptfoo eval -c evals/promptfooconfig.yaml` runs
end-to-end against the real pipeline.

### Phase 2 — Golden dataset
- 15 cases: anachronism traps per theme, seeded ingredients (fantasy/sci_fi/mythological),
  constraint adherence (vegetarian, prep-time, servings), 3–5 regression known-good recipes.
- Assertions:
  - `not-contains` banned ingredients per theme (anachronism)
  - `is-json` + recipe structure schema
  - `python`: iterations ≤ 3, report verdict present
  - `llm-rubric` "cookable and plausible" (judge temp 0.1)
  - `repeat: 3` on a subset → report pass@k vs pass^k (non-determinism honesty)

Acceptance: full suite runs; per-case pass/fail maps to the failure mode each case was
built to catch.

### Phase 3 — Docs & sample output
- README "Evaluating the pipeline" section: what's tested, run commands
  (`npx promptfoo eval`, `npx promptfoo view`), caveats.
- Commit a sample run output (JSON/markdown) so the harness is visible without running it.

Acceptance: a stranger can clone, run the evals, and read the pass rates.

### Phase 4 — Deferred
- CI gate via `promptfoo/promptfoo-action@v1` once evals are stable **and** an Ollama Cloud
  endpoint is reachable from GitHub Actions (a 31b model won't run on a runner).
- Trajectory evals (`trajectory:*`) if tool-choice ever becomes the risk.

## Pitfalls to avoid
- **Circular judge**: judge model ≈ generator model. Mitigate: temp 0.1, one dimension per
  rubric, "Unknown" fallback; be honest in README.
- **One-run noise**: a single trial is noise. Use `repeat`/multiple trials, report pass@k
  vs pass^k.
- **Live-API flakiness**: correlated failures look like agent bugs. If it becomes noise,
  mock the HTTP clients in eval mode (deterministic mode).
- **Eval saturation**: at 100% the suite stops giving signal — add harder cases. Treat the
  dataset as a living artifact.
- **Overclaiming**: in README, cite OpenAI's migration cookbook, not "Anthropic endorses
  Promptfoo".