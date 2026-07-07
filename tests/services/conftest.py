import pytest

from src.services import database as db


@pytest.fixture(autouse=True)
def mock_db():
    with pytest.MonkeyPatch.context() as m:
        m.setattr(db.settings, "database_url", "sqlite://")
        db.init_db()
        yield
