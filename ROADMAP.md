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

### Phase 3: External API Integration (Day 5)

- [x] USDA FoodData Central API client (httpx, async)
- [x] TheMealDB API client (httpx, async)
- [x] Agent tools via LangChain @tool decorator (agent-discoverable, schema-validated)
- [x] Tools: nutrition lookup, recipe pattern extraction, technique aggregation
- [x] Tests: API client mock/unit + agent tool integration tests

### Phase 4: Agent System

- [x] Planner Agent. Constraint extraction, technique identification
- [x] Creator Agent. Recipe generation with knowledge fusion
- [x] Critic Agent. Validation (lore, science, cookability)
- [x] Tests: agent unit tests per agent (6 tests, mocked LLM)

### Phase 5: Output & API

- [x] Structured JSON output (recipe + plausibility report)
- [x] FastAPI endpoints, error handling, LangSmith tracing
- [x] Tests: API route integration tests

### Phase 6: Polish & Deploy

- [ ] Integration + e2e tests, CI/CD (GitHub Actions)
- [ ] Railway deploy, demo recordings, architecture diagram, talking points

## Milestones

- **M1** (Day 2): Ingredient DB operational, basic API skeleton
- **M2** (Day 5): Full knowledge pipeline (SQL + RAG + External APIs) working
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
