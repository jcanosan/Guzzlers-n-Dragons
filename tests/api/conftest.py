"""API test fixtures — seeds in-memory DB for route integration tests."""

import pytest


@pytest.fixture(autouse=True, scope="session")
def seed_test_db():
    """Create and seed an in-memory database for all API tests.

    Runs once per session because all API tests share one app instance.
    The app's lifespan calls init_db; we redirect to in-memory SQLite
    before any test runs.
    """
    import src.services.database as db

    with pytest.MonkeyPatch.context() as m:
        m.setattr(db.settings, "database_url", "sqlite://")
        db.init_db()

        session = db.get_session()
        session.add_all([
            db.FictionalIngredientORM(
                name="lembas", description="Elven waybread",
                thematic_group="high_fantasy", texture="cake",
                rarity="rare",
                real_world_approximations=[
                    {"ingredient": "flour", "reasoning": "common"}
                ],
            ),
        ])
        session.commit()
        session.close()
        yield
