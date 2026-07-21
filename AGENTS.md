# Agent Instructions: Guzzlers-n-Dragons

## Documentation index
- [Roadmap](ROADMAP.md) - 12-day dev plan
- [Readme](README.md) - Explanation on this project and how to set it up
- [Technical Design](TECHNICAL_DESIGN.md) - Detailed architecture, data flow, API contracts

## Core Tech Stack
- **Runtime**: Python 3.14 (via `uv`)
- **LLM/Embeddings**: Ollama (`gemma4:31b-cloud` chat, `nomic-embed-text` embeddings)
- **Orchestration**: LangGraph (Planner $\to$ Creator $\to$ Critic)
- **Data**: SQLite (Structured Lore) + ChromaDB (Cooking Science RAG) + External APIs (USDA/TheMealDB)
- **API**: FastAPI

## Developer Commands
- **Environment**: `uv sync` (Install/Update)
- **Data Seeding**: `PYTHONPATH=. uv run python scripts/run_seeds.py` (Run before app start)
- **Run App**: `uv run uvicorn src.main:app --reload`
- **Lint**: `uv run ruff check .`
- **Format**: `uv run ruff format .`
- **Typecheck**: `uv run ty check .`
- **Test**: `uv run pytest -v`

## Architecture Nuances
- **Agent Loop**: Use LangGraph for Critic $\to$ Planner feedback loop. Do not implement as a simple chain.
- **Knowledge Access**: 
  - SQL $\to$ Lore & Ingredient profiles.
  - RAG $\to$ Culinary techniques & food science.
  - External APIs $\to$ Nutrition & real-world recipe patterns.
- **Plausibility**: `Critic` validate against `thematic_group` (high_fantasy, sci_fi, mythological). Prevent anachronisms (e.g., no potatoes in high fantasy).

## Constraints & Conventions
- **Typing**: Strict ty. Type hints on all functions.
- **Logging**: `structlog` for JSON logging.
- **Env**: Secrets/configs in `.env` via `src.config.settings`.
- **Data**: DB at `data/ingredients.db`, Vector store at `data/chroma`.
