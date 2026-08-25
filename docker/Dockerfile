# Build stage
FROM python:3.14-slim AS builder

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Test build stage (includes dev deps for pytest)
FROM python:3.14-slim AS builder-test

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --extra dev

# Test stage
FROM python:3.14-slim AS test

WORKDIR /app

COPY --from=builder-test /app/.venv .venv
COPY --from=builder-test /bin/uv /bin/uv
COPY src/ ./src/
COPY tests/ ./tests/
COPY data/ ./data/
COPY scripts/ ./scripts/
COPY pyproject.toml ./

ENV PATH="/app/.venv/bin:$PATH"

# Seed SQLite so tests can read ingredients + recipe patterns
# ingest_cooking_science skipped: needs live Ollama embeddings, mocked in tests
RUN PYTHONPATH=/app python scripts/seed_fictional_ingredients.py \
    && PYTHONPATH=/app python scripts/seed_real_ingredients.py \
    && PYTHONPATH=/app python scripts/seed_recipe_patterns.py

CMD ["pytest", "-v"]

# Runtime stage
FROM python:3.14-slim

WORKDIR /app

# Copy uv and virtual environment
COPY --from=builder /app/.venv .venv
COPY --from=builder /bin/uv /bin/uv

# Copy application code
COPY src/ ./src/
COPY data/ ./data/
COPY scripts/ ./scripts/

# Set PATH to use venv
ENV PATH="/app/.venv/bin:$PATH"

# Expose port
EXPOSE 8000

# Health check (curl not present in slim image; use stdlib urllib)
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD sh -c "python -c \"import os,urllib.request; urllib.request.urlopen('http://localhost:'+os.environ.get('PORT','8000')+'/health')\" || exit 1"

# Run application (Railway injects PORT; default 8000 for local/compose)
CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}"]