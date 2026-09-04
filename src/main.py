import os
from contextlib import asynccontextmanager
from pathlib import Path

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from src.api.routes import limiter
from src.api.routes import router as alchemy_router
from src.config.logging import configure_logging
from src.config.settings import settings
from src.services.database import init_db
from src.services.vector_store import vector_store

configure_logging()

logger = structlog.get_logger()

STATIC_DIR = Path(__file__).parent / "static"


async def rate_limit_handler(request: Request, exc: Exception) -> JSONResponse:
    """Return a 429 for slowapi RateLimitExceeded errors."""
    return JSONResponse(
        status_code=429, content={"detail": "Rate limit exceeded"}
    )


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to every response.

    - X-Content-Type-Options: nosniff — stop browsers from MIME-sniffing
      JSON/HTML responses into scripts.
    - X-Frame-Options: DENY — block clickjacking; no page here is meant
      to be framed.
    - Referrer-Policy: strict-origin-when-cross-origin — keep the URL out
      of external requests, still send origin on HTTPS-to-HTTPS.
    - Permissions-Policy — disable camera/mic/geolocation we never use.
    - Strict-Transport-Security: max-age=31536000 — browsers honor HSTS
      only over a secure connection, so setting it unconditionally is
      harmless on plain HTTP and removes a spoofable trust boundary.
    """

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )
        response.headers["Strict-Transport-Security"] = "max-age=31536000"
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "starting_application",
        ollama_host=os.environ.get("OLLAMA_HOST", "not set"),
        ollama_key_set=bool(os.environ.get("OLLAMA_API_KEY")),
    )
    init_db()
    vector_store.init()
    yield
    logger.info("shutting_down_application")


app = FastAPI(
    title="Guzzlers-n-Dragons",
    description=(
        "AI recipe alchemist transforming fictional ingredients into cookable "
        "recipes"
    ),
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

app.add_middleware(SecurityHeadersMiddleware)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
app.add_middleware(SlowAPIMiddleware)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "guzzlers-n-dragons"}


@app.get("/", response_class=FileResponse)
async def root():
    return FileResponse(STATIC_DIR / "index.html")


app.include_router(alchemy_router, prefix="/alchemy", tags=["alchemy"])
