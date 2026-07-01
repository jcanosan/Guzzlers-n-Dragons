# Guzzlers-n-Dragons Development Roadmap

## Project Vision

AI recipe alchemist transforming fictional ingredients into cookable recipes with thematic lore consistency and real-world food science.

## Timeline: 12 Days

### Phase 1: Foundation & Data Layer (Days 1-2)

- [x] Project scaffolding: pyproject, config, logging, Docker
- [ ] Build fictional ingredient DB: 30+ ingredients across 3 themes
  - High Fantasy: lembas, miruvor, cram, honey-cakes, elven wine
  - Sci-Fi: spice melange, romulan ale, synthehol, gagh, blue milk
  - Mythological: ambrosia, nectar, soma, golden apples, mead of poetry
- [ ] Seed real ingredient substitutions (USDA subset)

### Phase 2: RAG Pipeline (Days 3-4)

- [ ] Setup ChromaDB, ingest cooking science docs
  - The Food Lab excerpts (technique explanations)
  - On Food and Cooking fundamentals
  - Serious Eats guides (emulsification, Maillard, gelatinization)
  - Flavor pairing & substitution charts
- [ ] Build hybrid retriever (vector + keyword)
- [ ] Create tools: technique substitution, flavor pairing, texture modification

### Phase 3: MCP Integration (Day 5)

- [ ] USDA FoodData Central MCP client (nutrition, allergens)
- [ ] Custom TheMealDB wrapper (real recipe pattern extraction)
- [ ] Tools: get nutrition, find patterns by ingredient, common techniques

### Phase 4: Agent System (Days 6-8)

- [ ] Day 6: Planner Agent - constraint extraction, technique identification
- [ ] Day 7: Creator Agent - novel recipe generation with knowledge fusion
- [ ] Day 8: Critic Agent - validation (lore, science, cookability)

### Phase 5: Output & API (Days 9-10)

- [ ] Day 9: Structured JSON output (recipe + plausibility report)
- [ ] Day 10: FastAPI endpoints, error handling, LangSmith tracing

### Phase 6: Polish & Deploy (Days 11-12)

- [ ] Day 11: Tests, CI/CD (GitHub Actions: lint, typecheck, test)
- [ ] Day 12: Railway deploy, demo recordings, architecture diagram, talking points

## Milestones

- **M1** (Day 2): Ingredient DB operational, basic API skeleton
- **M2** (Day 5): Full knowledge pipeline (SQL + RAG + MCP) working
- **M3** (Day 8): Agent loop functional end-to-end
- **M4** (Day 10): API complete, validated outputs
- **M5** (Day 12): Deployed, documented, demo-ready

## Success Criteria

- [ ] Transforms 3+ fictional ingredients across all themes
- [ ] Output passes critic validation (lore + science + cookability)
- [ ] Substitutions are practical and explained
- [ ] API responds < 5s for typical requests
- [ ] 80%+ test coverage on core logic
- [ ] Clean mypy/ruff on all source files
