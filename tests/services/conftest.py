import pytest
from sqlalchemy.pool import StaticPool

from src.services import database as db


@pytest.fixture(autouse=True)
def mock_db():
    """Redirect database to in-memory SQLite for all service tests.

    autouse=True in conftest so every test (database, vector store,
    USDA, TheMealDB, tools) gets an isolated DB without opt-in.
    Thread-safe per-function via MonkeyPatch.context() auto-cleanup.
    """
    real_create_engine = db.create_engine

    def _test_engine(url, **kwargs):
        if url == "sqlite://":
            kwargs.setdefault("connect_args", {"check_same_thread": False})
            kwargs["poolclass"] = StaticPool
        return real_create_engine(url, **kwargs)

    with pytest.MonkeyPatch.context() as m:
        m.setattr(db.settings, "database_url", "sqlite://")
        m.setattr(db, "create_engine", _test_engine)
        db.init_db()
        yield
