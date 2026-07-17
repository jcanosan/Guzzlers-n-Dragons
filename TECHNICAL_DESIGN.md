# Guzzlers-n-Dragons Technical Design

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        FastAPI Layer                            │
│  POST /alchemy/transform    GET /alchemy/ingredients            │
│  GET /health                                                    │
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
   - Checks nutrition sanity via USDA API
   - Validates magical/extraordinary claims have lore justification
   - Outputs: Final recipe + detailed plausibility report
5. **Response**: Structured JSON with recipe, substitutions, nutrition, validation notes

## Agent Responsibilities

### Planner Agent

- **Input**: AlchemyRequest (ingredient, meal_type, theme, constraints)
- **Output**: PlannerResult (technique_requirements, flavor_profile, texture_goals, constraint_summary, knowledge_queries)
- **Tools**: SQL ingredient lookup, constraint analyzer

### Creator Agent

- **Input**: PlannerResult + retrieved knowledge
- **Output**: DraftRecipe (ingredients, instructions, description, plausibility_notes)
- **Tools**: RAG retriever (technique, pairing, substitution), API pattern extractor

### Critic Agent

- **Input**: DraftRecipe + original request + ingredient lore
- **Output**: ValidatedRecipe + PlausibilityReport (issues, substitutions, nutrition)
- **Tools**: Thematic validator, cookability checker, USDA nutrition verifier

## Knowledge Base Design

### SQL Database (SQLite)

```sql
-- Fictional ingredients with thematic grouping
CREATE TABLE fictional_ingredients (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    thematic_group TEXT NOT NULL,  -- 'high_fantasy', 'sci_fi', 'mythological'
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

- **Collections**: `cooking_techniques`, `flavor_pairings`, `substitution_rules`, `food_science`
- **Chunking**: ~500 tokens with 50-token overlap
- **Embedding**: `nomic-embed-text`
- **Metadata**: `source`, `category`, `technique_type`, `difficulty`

### External API Integration

Currently, each external data source (USDA, Fineli, Open Food Facts, TheMealDB)
is accessed via a plain `httpx` async client. Agent-facing tools are declared
with LangChain's `@tool` decorator — same semantics as MCP (name, description,
structured schema), but without the MCP wire protocol.

- **USDA FoodData Central**: Nutrition lookup, allergen data
- **TheMealDB Wrapper**:
  - Normalizes API responses to pattern format
  - Extracts: techniques by ingredient, common pairings, meal type distributions
  - Caches locally to reduce API calls

#### Future: Standalone MCP servers

Each data source will become its own MCP server in a separate repository:

```
usda-mcp-server/       ← stdio JSON-RPC server wrapping USDA REST API
fineli-mcp-server/     ← stdio JSON-RPC server wrapping Fineli REST API
off-mcp-server/        ← stdio JSON-RPC server wrapping Open Food Facts API
```

This project will then load them via `langchain-mcp-adapters.load_mcp_tools()`
instead of importing the HTTP clients directly. The `nutrition.py` orchestration
layer and `agent_tools.py` @tool wrappers survive unchanged — only the transport
layer swaps.

## Validation System

### Thematic Consistency Checks

```python
# Anachronism detection per theme
THEMATIC_CONSTRAINTS = {
    "high_fantasy": {
        "forbidden": ["tomato", "potato", "corn", "chocolate", "chili_pepper"],
        "tech_level": "pre_industrial",
        "allowed_magic": "ingredient_based"
    },
    "sci_fi": {
        "forbidden": [],
        "tech_level": "advanced",
        "allowed_magic": "technological"
    },
    "mythological": {
        "forbidden": [],
        "tech_level": "ancient",
        "allowed_magic": "divine"
    }
}
```

### Cookability Validation

- Instruction clarity (imperative mood, specific actions)
- Time/temperature reasonableness
- Equipment availability for theme
- Ingredient quantity plausibility

### Nutrition Sanity

- Calorie estimates via USDA for real ingredients
- Magical ingredients: flagged as "unknown" with lore-based estimates
- Warning if claimed effects contradict nutrition science

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
    "substitutions": [{"for": "...", "options": [...]}],
    "nutrition_estimate": {"calories_per_serving": 22, "notes": "..."},
    "validation_issues": [...]
  },
  "metadata": {
    "processing_time_ms": 1234,
    "agent_trace_id": "langsmith-trace-uuid"
  }
}
```

## Tech Stack Justification

| Layer         | Choice              | Rationale                                       |
| ------------- | ------------------- | ----------------------------------------------- |
| API           | FastAPI             | Async, auto-docs, type-safe, production-ready   |
| Orchestration | LangGraph           | Explicit state graph, supports validation loops |
| LLM           | TBD                 | Cost/quality balance for creative generation    |
| SQL           | SQLite + SQLAlchemy | Zero-config, portable, ACID                     |
| Vector DB     | ChromaDB            | Local, persistent, good LangChain integration   |
| External APIs | USDA + TheMealDB    | Live nutrition + real recipe patterns           |
| Validation    | Pydantic + custom   | Type-safe at boundaries, domain logic separate  |
| Deploy        | Railway (Docker)    | Free tier, GitHub CI/CD, auto-deploy            |
| Observability | LangSmith           | Trace agent reasoning for demos                 |

## Extensibility Points

1. **New Themes**: Add entry to `THEMATIC_CONSTRAINTS` + seed ingredients
2. **New Knowledge Sources**: Package as an API clients as MCP servers in their
   own repos, then load via `langchain-mcp-adapters.load_mcp_tools()`.
3. **New Meal Types**: Add pattern to `recipe_patterns` table
4. **Output Formats**: Add formatter in `output_tools.py` (PDF, HTML, etc.)
5. **Validation Rules**: Extend Critic with new checker classes
