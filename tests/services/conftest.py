import pytest

from src.services import database as db


@pytest.fixture(autouse=True)
def mock_db():
    """Redirect database to in-memory SQLite for all service tests.

    autouse=True in conftest so every test (database, vector store,
    USDA, TheMealDB, tools) gets an isolated DB without opt-in.
    Thread-safe per-function via MonkeyPatch.context() auto-cleanup.
    """
    with pytest.MonkeyPatch.context() as m:
        m.setattr(db.settings, "database_url", "sqlite://")
        db.init_db()
        yield
