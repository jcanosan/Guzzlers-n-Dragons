import structlog
from sqlalchemy import JSON, Integer, String, Text, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import (
    Mapped,
    Session,
    declarative_base,
    mapped_column,
    sessionmaker,
)

from src.config.settings import settings
from src.schemas.domain import (
    FictionalIngredient,
    RealIngredient,
    RecipePattern,
)

logger = structlog.get_logger()

Base = declarative_base()


class FictionalIngredientORM(Base):
    """Object-Relational Mapping (ORM) model for fictional ingredients from
    game/movie universes."""

    __tablename__ = "fictional_ingredients"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    description: Mapped[str | None] = mapped_column(Text, default=None)
    thematic_group: Mapped[str] = mapped_column(
        String(30), nullable=False, index=True
    )
    taste_profile: Mapped[dict] = mapped_column(JSON, default={})
    texture: Mapped[str | None] = mapped_column(String(50), default=None)
    rarity: Mapped[str] = mapped_column(String(20), default="common")
    magical_properties: Mapped[str | None] = mapped_column(Text, default="")
    preparation_notes: Mapped[str | None] = mapped_column(Text, default="")
    real_world_approximations: Mapped[list[dict]] = mapped_column(
        JSON, default=[]
    )


class RealIngredientORM(Base):
    """ORM model for real-world ingredients with optional USDA FDC link."""

    __tablename__ = "real_ingredients"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    usda_fdc_id: Mapped[int | None] = mapped_column(
        Integer, unique=True, nullable=True
    )
    category: Mapped[str] = mapped_column(String(50), default="")
    nutrition_per_100g: Mapped[dict] = mapped_column(JSON, default={})


class RecipePatternORM(Base):
    """ORM model for parameterized recipe templates keyed by meal type."""

    __tablename__ = "recipe_patterns"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    meal_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )
    pattern_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    example_ingredients: Mapped[list[str]] = mapped_column(JSON, default=[])


engine: Engine | None = None
SessionLocal: sessionmaker[Session] | None = None


def init_db() -> None:
    """Create engine, session factory, and all tables."""
    global engine, SessionLocal
    engine = create_engine(settings.database_url, echo=settings.debug)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    logger.info("database_initialized", url=settings.database_url)


def get_session() -> Session:
    """Get a SQLAlchemy session. If none exists initialize the DB."""
    if SessionLocal is None:
        init_db()

    factory = SessionLocal
    if factory is None:
        raise RuntimeError("Database failed to initialize")
    return factory()


def get_ingredient_by_name(name: str) -> FictionalIngredient | None:
    """Fetch a single fictional ingredient by name. Returns None if missing."""
    db = get_session()
    try:
        orm = (
            db.query(FictionalIngredientORM)
            .filter(FictionalIngredientORM.name == name)
            .first()
        )
        if orm:
            return FictionalIngredient(
                id=orm.id,
                name=orm.name,
                description=orm.description or "",
                thematic_group=orm.thematic_group,
                taste_profile=orm.taste_profile or {},
                texture=orm.texture or "",
                rarity=orm.rarity,
                magical_properties=orm.magical_properties or "",
                preparation_notes=orm.preparation_notes or "",
                real_world_approximations=orm.real_world_approximations or [],
            )
        return None
    finally:
        db.close()


def list_ingredients(
    thematic_group: str | None = None,
) -> list[FictionalIngredient]:
    """List all fictional ingredients, optionally filtered by thematic group."""
    db = get_session()
    try:
        query = db.query(FictionalIngredientORM)
        if thematic_group:
            query = query.filter(
                FictionalIngredientORM.thematic_group == thematic_group
            )
        orms = query.all()
        return [
            FictionalIngredient(
                id=orm.id,
                name=orm.name,
                description=orm.description or "",
                thematic_group=orm.thematic_group,
                taste_profile=orm.taste_profile or {},
                texture=orm.texture or "",
                rarity=orm.rarity,
                magical_properties=orm.magical_properties or "",
                preparation_notes=orm.preparation_notes or "",
                real_world_approximations=orm.real_world_approximations or [],
            )
            for orm in orms
        ]
    finally:
        db.close()


def seed_fictional_ingredients(ingredients: list[FictionalIngredient]) -> int:
    """Insert fictional ingredients, skip duplicates. Returns new row count."""
    db = get_session()
    count = 0
    try:
        for ing in ingredients:
            exists = (
                db.query(FictionalIngredientORM)
                .filter(FictionalIngredientORM.name == ing.name)
                .first()
            )
            if not exists:
                orm = FictionalIngredientORM(
                    name=ing.name,
                    description=ing.description,
                    thematic_group=ing.thematic_group,
                    taste_profile=ing.taste_profile,
                    texture=ing.texture,
                    rarity=ing.rarity,
                    magical_properties=ing.magical_properties,
                    preparation_notes=ing.preparation_notes,
                    real_world_approximations=ing.real_world_approximations,
                )
                db.add(orm)
                count += 1
        db.commit()
        logger.info("seeded_fictional_ingredients", count=count)
        return count
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("seed_failed", error=str(e))
        raise
    finally:
        db.close()


def seed_real_ingredients(ingredients: list[RealIngredient]) -> int:
    """Insert real ingredients, skip duplicates. Returns new row count."""
    db = get_session()
    count = 0
    try:
        for ing in ingredients:
            exists = (
                db.query(RealIngredientORM)
                .filter(RealIngredientORM.name == ing.name)
                .first()
            )
            if not exists:
                orm = RealIngredientORM(
                    name=ing.name,
                    usda_fdc_id=ing.usda_fdc_id,
                    category=ing.category,
                    nutrition_per_100g=ing.nutrition_per_100g,
                )
                db.add(orm)
                count += 1
        db.commit()
        logger.info("seeded_real_ingredients", count=count)
        return count
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("seed_failed", error=str(e))
        raise
    finally:
        db.close()


def seed_recipe_patterns(patterns: list[RecipePattern]) -> int:
    """Insert recipe patterns, skip duplicates. Returns new row count."""
    db = get_session()
    count = 0
    try:
        for pat in patterns:
            exists = (
                db.query(RecipePatternORM)
                .filter(RecipePatternORM.meal_type == pat.meal_type)
                .first()
            )
            if not exists:
                orm = RecipePatternORM(
                    meal_type=pat.meal_type,
                    pattern_json=pat.pattern_json,
                    example_ingredients=pat.example_ingredients,
                )
                db.add(orm)
                count += 1
        db.commit()
        logger.info("seeded_recipe_patterns", count=count)
        return count
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("seed_failed", error=str(e))
        raise
    finally:
        db.close()
