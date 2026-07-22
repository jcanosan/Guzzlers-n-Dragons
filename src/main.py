from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from src.api.routes import router as alchemy_router
from src.config.logging import configure_logging
from src.config.settings import settings
from src.services.database import init_db
from src.services.vector_store import vector_store

configure_logging()

logger = structlog.get_logger()


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to every response.

    HSTS left commented — uncomment only when TLS terminates in front
    of the app (Cloudflare, Railway TLS proxy, etc.).
    """

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )
        # response.headers["Strict-Transport-Security"] = (
        #     "max-age=31536000; includeSubDomains"
        # )
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("starting_application")
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


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "guzzlers-n-dragons"}


@app.get("/")
async def root():
    return {
        "name": "Guzzlers-n-Dragons",
        "description": "Transform fictional ingredients into plausible recipes",
        "version": "0.1.0",
        "docs": "/docs",
        "endpoints": {
            "transform": "/alchemy/transform",
            "ingredients": "/alchemy/ingredients",
            "health": "/health",
        },
    }


app.include_router(alchemy_router, prefix="/alchemy", tags=["alchemy"])
