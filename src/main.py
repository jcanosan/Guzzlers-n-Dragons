from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router as alchemy_router
from src.services.database import init_db
from src.services.vector_store import init_vector_store

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("starting_application")
    init_db()
    init_vector_store()
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
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
