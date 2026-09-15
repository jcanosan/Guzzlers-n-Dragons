# Portfolio Demo Plan

Goal: showcase the Planner → Creator → Critic agent loop as an agent-engineering portfolio piece. The visual, stage-by-stage loop is the differentiator — it separates this from a thin LLM wrapper.

## Key technical insight

`/alchemy/transform` (routes.py:95) is one-shot `ainvoke` — returns only the final result. Both the CLI trace (Phase 2) and the live page (Phase 3) need LangGraph's `astream(stream_mode="updates")`, which emits each node's output as it completes. That trace helper is the shared building block; build it once in Phase 2, reuse in Phase 3.

## Model backend

`gemma4:31b-cloud` runs cloud-side (no local Ollama dependency). Live demo needs `OLLAMA_HOST`/`OLLAMA_API_KEY` + USDA/TheMealDB keys in the deploy env. External API keys may be absent in prod → pipeline must degrade gracefully (verify).

## Phases

### Phase 1 — README + visuals (shipped)
- Replace ASCII block in `README.md:20-29` with Mermaid diagram of Planner→Creator→Critic including Critic→Planner feedback loop arrow.
- shields.io badges: Python version, uv, license, live-demo link (placeholder until Phase 3).
- One-line pitch above fold + "why these choices" section (why RAG over fine-tuning, why LangGraph over a chain).

Acceptance: stranger understands the pipeline and can run it within 60 seconds of reading.

### Phase 2 — Demo CLI + terminal GIF (shipped)
- New `scripts/demo.py`: runs one transform via `astream`, prints readable trace (Planner plan → Creator draft → Critic verdict → iteration count). Commit sample output to `examples/`.
- Record CLI run (asciinema+agg or vhs) → embed GIF in README.

Acceptance: `PYTHONPATH=. uv run python scripts/demo.py --ingredient "spice melange" --theme sci_fi` prints a readable loop trace.

### Phase 3 — Hosted live demo, FastAPI page + SSE (shipped)
- `POST /alchemy/transform/stream` (SSE) via `astream(stream_mode="updates")` → `node` event per completed stage (curated payload), then `done`; `error` on timeout/failure.
- Static HTML/JS page at `/` (FastAPI-served): form for ingredient / meal type / theme / constraints + agent-trace panel that lights up each node as it runs; recipe + plausibility report render on completion. Replaces current JSON root.
- `slowapi` rate limit on public endpoint + spend cap via settings.
- Deploy to Railway (`railway.json` + Dockerfile exist). Verify env + graceful degradation without external API keys.

Acceptance: public URL; pick "spice melange", watch the loop run, get a cookable recipe.

### Phase 4 — marimo notebook walkthrough, optional (skipped)
- `notebooks/demo.py`: theme selector, run pipeline stage-by-stage, show RAG-retrieved docs + Critic feedback. Deployable via `marimo run`.

Acceptance: reviewer changes theme fantasy→sci_fi, sees the loop re-run and respond.
Skip if time tight — Phases 1–3 carry the portfolio.

### Phase 5 — Video, polish (Skipped)
- 60–90s clip of live demo: result in first 15s, then loop running with intermediate states, one tradeoff explained, CTA.
- OBS/Loom + ffmpeg. Embed as clickable thumbnail in README.

## Sequencing
1 → 2 → 3 → 4 → 5. Phase 2's trace helper is the foundation for Phase 3's SSE stream — don't skip it.

## Pitfalls to avoid
- API keys in code/commit history (run `git log -p | grep -i api_key` before going public)
- Uncontrolled cost — rate limit + spend caps
- Model not reproducible — name model + version in README
- Cold starts on free tier — handle loading states
- Overclaiming — be precise about what is built vs. borrowed
- Dead links / private repos — verify every URL before sharing
