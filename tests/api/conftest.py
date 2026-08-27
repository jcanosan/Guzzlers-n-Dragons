"""API test fixtures — seeds in-memory DB for route integration tests."""

import pytest
from sqlalchemy.pool import StaticPool


@pytest.fixture(autouse=True, scope="session")
def seed_test_db():
    """Create and seed an in-memory database for all API tests.

    Runs once per session because all API tests share one app instance.
    The app's lifespan calls init_db; we redirect to in-memory SQLite
    before any test runs. StaticPool pins all connections to the same
    in-memory DB.
    """
    import src.services.database as db

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

        session = db.get_session()
        session.add_all(
            [
                db.FictionalIngredientORM(
                    name="lembas",
                    description="Elven waybread",
                    thematic_group="fantasy",
                    texture="cake",
                    rarity="rare",
                    real_world_approximations=[
                        {"ingredient": "flour", "reasoning": "common"}
                    ],
                ),
            ]
        )
        session.commit()
        session.close()
        yield
