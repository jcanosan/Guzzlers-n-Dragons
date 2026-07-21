# Guzzlers-n-Dragons

AI recipe alchemist that transforms fictional ingredients (e.g. from books, games, films...) into plausible, cookable recipes. It aims to respect thematic lore, technology level, and culinary culture while applying real-world food science.

## Highlights

- **Multi-agent orchestration** (LangGraph): Planner → Creator → Critic with validation loop
- **Knowledge fusion**: SQL (structured lore) + RAG (cooking science) + External APIs (live data)
- **Constraint-aware generation**: Dietary, time, equipment, thematic consistency
- **Production patterns**: Async FastAPI, Pydantic validation, Docker, CI/CD, observability

## Thematic Groups

- **high_fantasy**: Lembas, miruvor, cram, honey-cakes, elven wine
- **sci_fi**: Spice melange, Romulan ale, synthehol, gagh, blue milk
- **mythological**: Ambrosia, nectar, soma, golden apples, mead of poetry

## Architecture

```
FastAPI → LangGraph (Planner → Creator → Critic)
                ↓
    ┌───────────┼───────────┐
    ▼           ▼           ▼
    SQL        RAG        API
Ingredients  Science    USDA + TheMealDB
```

## Design docs

- [Roadmap](ROADMAP.md) - 12-day development plan
- [Technical Design](TECHNICAL_DESIGN.md) - Detailed architecture, data flow and API contracts

## Quick Start

```bash
# Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone <repo-url>
cd Guzzlers-n-Dragons

# Create virtual environment and install dependencies
uv sync

# Copy environment file and add your API keys
cp .env.example .env

# Seed the DB with fictional ingredients, real ingredients, and recipe patterns
PYTHONPATH=. uv run python scripts/run_seeds.py

# Run the API server
uv run uvicorn src.main:app --reload
```

API available at `http://localhost:8000` with docs at `http://localhost:8000/docs`.

## Docker

```bash
# Build and run
docker compose -f docker/docker-compose.yml up --build

# Run tests
docker compose -f docker/docker-compose.yml --profile testing run test
```

## API Endpoints

| Method | Endpoint                      | Description                                |
| ------ | ----------------------------- | ------------------------------------------ |
| POST   | `/alchemy/transform`          | Transform fictional ingredient into recipe |
| GET    | `/alchemy/ingredients`        | List all fictional ingredients             |
| GET    | `/alchemy/ingredients/{name}` | Get ingredient details                     |
| GET    | `/health`                     | Health check                               |

## Example Request

```bash
curl -X POST http://localhost:8000/alchemy/transform \
  -H "Content-Type: application/json" \
  -d '{
    "fictional_ingredient": "spice melange",
    "meal_type": "beverage",
    "thematic_group": "sci_fi",
    "constraints": {
      "servings": 4,
      "max_prep_time_minutes": 15,
      "dietary": ["vegetarian"]
    }
  }'
```

## License

[MIT](LICENSE)
