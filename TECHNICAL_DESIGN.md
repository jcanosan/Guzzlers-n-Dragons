# Guzzlers-n-Dragons Technical Design

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        FastAPI Layer                            │
│  POST /alchemy/transform    GET /alchemy/ingredients            │
│  GET /alchemy/ingredients/{name}    GET /health                 │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LangGraph Agent System                       │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  │  Planner    │───▶│  Creator    │───▶│  Critic     │          │
│  │  Agent      │    │  Agent      │    │  Agent      │          │
│  └─────────────┘    └─────────────┘    └─────────────┘          │
│       │                   │                   │                 │
│       ▼                   ▼                   ▼                 │
│  Constraint         Knowledge            Validation             │
│  Analysis           Fusion               Loop                   │
└──────────────────────────────┬──────────────────────────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
       ┌────────────┐  ┌────────────┐  ┌────────────┐
       │   SQL      │  │   RAG      │  │   API      │
       │  Tools     │  │  Tools     │  │  Tools     │
       └────────────┘  └────────────┘  └────────────┘
```

## Data Flow

1. **Request Ingestion**: Client POSTs `{fictional_ingredient, meal_type, thematic_group, constraints}`
2. **Planner Phase**:
   - Extracts constraints (dietary, time, equipment)
   - Identifies required techniques from meal type
   - Queries SQL for ingredient profile + lore
   - Determines knowledge needs for Creator
3. **Creator Phase**:
   - Retrieves cooking science from RAG (technique, pairing, substitution)
   - Fetches real-world patterns from external APIs (TheMealDB)
   - Generates novel recipe using LLM + structured knowledge
   - Produces draft recipe + initial plausibility notes
4. **Critic Phase**:
   - Validates thematic consistency (anachronism check, tech level)
   - Verifies cookability (clear steps, reasonable times/temps)
   - Resolves the fictional ingredient to a real-world approximation
     (seeded → LLM → raw fallback), then checks nutrition via the
     USDA → Open Food Facts → DB chain
   - Validates magical/extraordinary claims have lore justification
   - Outputs: Final recipe + detailed plausibility report
5. **Response**: Structured JSON with recipe, substitutions, nutrition, validation notes

## Agent Responsibilities

### Planner Agent

- **Input**: AlchemyRequest (ingredient, meal_type, theme, constraints)
- **Output**: PlannerResult (technique_requirements, flavor_profile, texture_goals, constraint_summary, knowledge_queries)
- **Tools**: SQL ingredient + recipe-pattern lookup, RAG technique retrieval (constraint extraction via LLM)

### Creator Agent

- **Input**: PlannerResult + retrieved knowledge
- **Output**: DraftRecipe (ingredients, instructions, description, plausibility_notes)
- **Tools**: RAG retriever (technique, pairing, substitution), API pattern extractor

### Critic Agent

- **Input**: DraftRecipe + original request + ingredient lore
- **Output**: ValidatedRecipe + PlausibilityReport (issues, substitutions, nutrition)
- **Tools**: Thematic validator, cookability checker, nutrition approximation
  resolver + lookup chain (USDA → Open Food Facts → DB)

## Knowledge Base Design

### SQL Database (SQLite)

```sql
-- Fictional ingredients with thematic grouping
CREATE TABLE fictional_ingredients (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    thematic_group TEXT NOT NULL,  -- 'fantasy', 'sci_fi', 'mythological'
    taste_profile TEXT,            -- JSON: sweet/salty/umami/bitter/sour/spicy scores
    texture TEXT,                  -- e.g., 'powder', 'liquid', 'bread-like'
    rarity TEXT,                   -- 'common', 'rare', 'legendary'
    magical_properties TEXT,       -- Description of special effects
    preparation_notes TEXT,        -- Lore-based handling/prep guidance
    real_world_approximations TEXT -- JSON array of {ingredient, reasoning}
);

-- Real ingredients for substitution mapping (USDA subset)
CREATE TABLE real_ingredients (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    usda_fdc_id INTEGER,
    category TEXT,
    nutrition_per_100g TEXT        -- JSON with macros/micros
);

-- Recipe pattern templates by meal type
CREATE TABLE recipe_patterns (
    id INTEGER PRIMARY KEY,
    meal_type TEXT NOT NULL,       -- 'beverage', 'bread', 'stew', 'dessert', etc.
    pattern_json TEXT NOT NULL,    -- Parameterized template
    example_ingredients TEXT       -- JSON array of typical ingredients
);
```

### RAG Knowledge Base (ChromaDB)

- **Collection**: single `cooking_science` collection; documents split on `## ` headings,
  with large sections chunked to ~1000 chars and 200-char overlap
- **Embedding**: `BAAI/bge-small-en-v1.5` (FastEmbed, in-process)
- **Metadata**: `source`, `topic` (filename stem), `section`, `chunk`

### External API Integration

Currently, each external data source (USDA, Open Food Facts, TheMealDB)
is accessed via a plain `httpx` async client. Agent-facing tools are declared
with LangChain's `@tool` decorator.

- **USDA FoodData Central**: Nutrition lookup (food search + detail)
- **Open Food Facts**: Fallback nutrition source, no API key needed
- **TheMealDB Wrapper**:
  - Normalizes API responses to pattern format
  - Extracts: techniques by ingredient, ingredient pairings, and category/area

Eventually, MCP integrations are planned.

## Validation System

### Thematic Consistency Checks

```python
# Anachronism detection per theme
THEMATIC_CONSTRAINTS = {
    "fantasy": {
        "forbidden": ["tomato", "potato", "corn", "chocolate", "chili_pepper"],
        "tech_level": "pre_industrial",
        "allowed_magic": "ingredient_based",
    },
    "sci_fi": {
        "forbidden": [],
        "tech_level": "advanced",
        "allowed_magic": "technological",
    },
    "mythological": {
        "forbidden": [],
        "tech_level": "ancient",
        "allowed_magic": "divine",
    },
}
```

### Cookability Validation

- Instruction clarity (imperative mood, specific actions)
- Time/temperature reasonableness
- Equipment availability for theme
- Ingredient quantity plausibility

### Nutrition Sanity

- Fictional ingredients are resolved to a real-world approximation first:
  a seeded `real_world_approximations[0]["ingredient"]` if present, else an
  LLM mapping (strips fictional modifiers, e.g. "mutant cow milk" → "cow milk"),
  else the raw name as a last resort.
- Nutrition lookup chains USDA → Open Food Facts → seeded DB (`lookup_nutrition`).
- Approximated lookups are flagged in the report notes as `(approx: <term>)`.
- When every source misses, the estimate returns no macros with a
  "No real ingredients found for analysis" note.

## API Contract

### POST /alchemy/transform

**Request**:

```json
{
  "fictional_ingredient": "spice melange",
  "meal_type": "beverage",
  "thematic_group": "sci_fi",
  "constraints": {
    "servings": 4,
    "max_prep_time_minutes": 15,
    "dietary": ["vegetarian"],
    "equipment": ["stove", "pot"]
  }
}
```

**Response**:

```json
{
  "recipe": {
    "name": "Spice-Infused Clarity Tea",
    "description": "...",
    "ingredients": [{"item": "...", "amount": "...", "notes": "..."}],
    "instructions": ["1. ...", "2. ..."],
    "prep_time_minutes": 5,
    "cook_time_minutes": 0,
    "servings": 4,
    "difficulty": "easy"
  },
  "plausibility_report": {
    "thematic_consistency": "PASS|WARN|FAIL",
    "notes": [...],
    "substitutions": [],
    "nutrition_estimate": {
      "calories_per_serving": 22,
      "protein_g": 3.2,
      "carbs_g": 0.5,
      "fat_g": 0.1,
      "notes": "Source: usda (approx: <term>)"
    },
    "validation_issues": [{"type": "...", "severity": "HIGH", "message": "...", "suggestion": "..."}]
  },
  "metadata": {
    "iterations": 1,
    "ingredient": "spice melange"
  }
}
```

Note: as of now, `substitutions` is present in the response schema but the Critic does not currently populate it.

## Tech Stack Justification

| Layer         | Choice              | Rationale                                       |
| ------------- | ------------------- | ----------------------------------------------- |
| API           | FastAPI             | Async, auto-docs, type-safe, production-ready   |
| Orchestration | LangGraph           | Explicit state graph, supports validation loops |
| LLM           | Ollama (`gemma4:31b-cloud`) | Local/cloud LLM for creative generation     |
| SQL           | SQLite + SQLAlchemy | Zero-config, portable, ACID                     |
| Vector DB     | ChromaDB            | Local, persistent, good LangChain integration   |
| External APIs | USDA + TheMealDB    | Live nutrition + real recipe patterns           |
| Validation    | Pydantic + custom   | Type-safe at boundaries, domain logic separate  |
| Deploy        | Railway (Docker)    | Free tier, GitHub CI/CD, auto-deploy            |
| Observability | structlog           | JSON structured logging                         |

### CORS Configuration

CORS is configured via the `CORS_ORIGINS` environment variable.

- **Format**: JSON array of allowed origin strings.
- **Default**: `["http://localhost:5173"]` (Vite dev server).
- **Production**: Set to your deployed frontend URL(s), e.g.
  `["https://app.example.com"]`.
- **Security**: `allow_credentials=True` requires explicit origins. Do NOT use
  `["*"]` in production.

## Deployment

### Railway

The project includes a `docker/Dockerfile`; `railway.json` points Railway at it.

**Required environment variables** (set in Railway dashboard):

| Variable | Example | Notes |
|---|---|---|
| `LLM_MODEL` | `gemma4:31b-cloud` | Must resolve to a reachable Ollama instance |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama base URL (default); `https://api.ollama.com` for Ollama Cloud |
| `OLLAMA_API_KEY` | `your_api_key` | Required for Ollama Cloud; leave empty for a local Ollama |
| `CORS_ORIGINS` | `["https://app.example.com"]` | Your frontend's deployed origin |
| `DEBUG` | `false` | Disables `/docs` and `/redoc` when false |

**Optional environment variables:**

| Variable | What it enables |
|---|---|
| `USDA_API_KEY` | USDA nutrition lookups (api.data.gov) |
| `SQL_ECHO` | SQLAlchemy statement logging (dev only) |

**Deploy steps:**
1. Push to GitHub
2. Connect repo in Railway
3. Set env vars in Railway dashboard
4. Railway detects `docker/Dockerfile` and builds

### CI/CD

A GitHub Actions workflow runs on every push/PR (`.github/workflows/ci.yml`):
- `ruff check .` — Lint
- `ty check .` — Type check
- `pytest tests/` — Test suite

## Extensibility Points

1. **New Themes**: Add entry to `THEMATIC_CONSTRAINTS` + seed ingredients
2. **New Knowledge Sources**: Package as an API clients as MCP servers in their
   own repos, then load via `langchain-mcp-adapters.load_mcp_tools()`.
3. **New Meal Types**: Add pattern to `recipe_patterns` table
4. **Output Formats**: Add formatter in `output_tools.py` (PDF, HTML, etc.)
5. **Validation Rules**: Extend Critic with new checker classes
