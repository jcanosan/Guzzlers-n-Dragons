# Guzzlers-n-Dragons Development Roadmap

## Project Vision

AI recipe alchemist: transform fictional ingredients into cookable recipes with thematic lore consistency + real-world food science.

## Timeline

### Phase 1: Foundation & Data Layer

- [x] Project scaffolding: pyproject, config, logging, Docker
- [x] Build fictional ingredient DB: 15 ingredients across 3 themes
- [x] Seed real ingredient substitutions
- [x] Tests: settings, schemas, database CRUD and seeding

### Phase 2: RAG Pipeline

- [x] Setup ChromaDB, ingest cooking science docs
  - Technique substitution guide
  - Flavor pairing science
  - Texture modification & food chemistry
- [x] Hybrid retriever (vector + keyword)
- [x] Tools: technique substitution, flavor pairing, texture modification
- [x] Tests: vector store add/search/stats, tool functions

### Phase 3: MCP Integration

- [ ] USDA FoodData Central MCP client (nutrition, allergens)
- [ ] Custom TheMealDB wrapper (recipe pattern extraction)
- [ ] Tools: get nutrition, find patterns by ingredient, common techniques
- [ ] Tests: MCP client mock/unit

### Phase 4: Agent System

- [ ] Planner Agent. Constraint extraction, technique identification
- [ ] Creator Agent. Recipe generation with knowledge fusion
- [ ] Critic Agent. Validation (lore, science, cookability)
- [ ] Tests: agent unit tests per agent

### Phase 5: Output & API

- [ ] Structured JSON output (recipe + plausibility report)
- [ ] FastAPI endpoints, error handling, LangSmith tracing
- [ ] Tests: API route integration tests

### Phase 6: Polish & Deploy

- [ ] Integration + e2e tests, CI/CD (GitHub Actions)
- [ ] Railway deploy, demo recordings, architecture diagram, talking points

## Milestones

- **M1** (Day 2): Ingredient DB operational, basic API skeleton
- **M2** (Day 5): Full knowledge pipeline (SQL + RAG + MCP) working
- **M3** (Day 8): Agent loop functional end-to-end
- **M4** (Day 10): API complete, validated outputs
- **M5** (Day 12): Deployed, documented, demo-ready

## Success Criteria

- [ ] Transform 3+ fictional ingredients across all themes
- [ ] Output passes critic validation (lore + science + cookability)
- [ ] Substitutions are practical and explained
- [ ] API respond < 5s for typical requests
- [ ] 80%+ test coverage on core logic
- [ ] Clean ruff/ty on all source files
