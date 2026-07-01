import structlog
from sqlalchemy import JSON, Column, Integer, String, Text, create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from src.config.settings import settings
from src.schemas.domain import (
    FictionalIngredient,
    RealIngredient,
    RecipePattern,
)

logger = structlog.get_logger()

Base = declarative_base()


class FictionalIngredientORM(Base):
    __tablename__ = "fictional_ingredients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    thematic_group = Column(String(30), nullable=False, index=True)
    taste_profile = Column(JSON, default={})
    texture = Column(String(50))
    rarity = Column(String(20), default="common")
    magical_properties = Column(Text, default="")
    preparation_notes = Column(Text, default="")
    real_world_approximations = Column(JSON, default=[])


class RealIngredientORM(Base):
    __tablename__ = "real_ingredients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    usda_fdc_id = Column(Integer, unique=True, nullable=True)
    category = Column(String(50), default="")
    nutrition_per_100g = Column(JSON, default={})


class RecipePatternORM(Base):
    __tablename__ = "recipe_patterns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    meal_type = Column(String(50), nullable=False, index=True)
    pattern_json = Column(JSON, nullable=False)
    example_ingredients = Column(JSON, default=[])


engine = None
SessionLocal = None


def init_db() -> None:
    global engine, SessionLocal
    engine = create_engine(settings.database_url, echo=settings.debug)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    logger.info("database_initialized", url=settings.database_url)


def get_session() -> Session:
    if SessionLocal is None:
        init_db()
    return SessionLocal()


def get_ingredient_by_name(name: str) -> FictionalIngredient | None:
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
                description=orm.description,
                thematic_group=orm.thematic_group,
                taste_profile=orm.taste_profile or {},
                texture=orm.texture,
                rarity=orm.rarity,
                magical_properties=orm.magical_properties,
                preparation_notes=orm.preparation_notes,
                real_world_approximations=orm.real_world_approximations or [],
            )
        return None
    finally:
        db.close()


def list_ingredients(
    thematic_group: str | None = None,
) -> list[FictionalIngredient]:
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
                description=orm.description,
                thematic_group=orm.thematic_group,
                taste_profile=orm.taste_profile or {},
                texture=orm.texture,
                rarity=orm.rarity,
                magical_properties=orm.magical_properties,
                preparation_notes=orm.preparation_notes,
                real_world_approximations=orm.real_world_approximations or [],
            )
            for orm in orms
        ]
    finally:
        db.close()


def seed_fictional_ingredients(ingredients: list[FictionalIngredient]) -> int:
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
