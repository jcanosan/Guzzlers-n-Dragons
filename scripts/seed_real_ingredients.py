#!/usr/bin/env python3
"""Seed common real ingredients for substitution mapping."""

from src.schemas.domain import RealIngredient
from src.services.database import init_db, seed_real_ingredients

COMMON_INGREDIENTS = [
    # Grains & Flours
    RealIngredient(
        name="all-purpose flour",
        category="grain",
        nutrition_per_100g={
            "calories": 364,
            "protein": 10,
            "carbs": 76,
            "fat": 1,
        },
    ),
    RealIngredient(
        name="whole wheat flour",
        category="grain",
        nutrition_per_100g={
            "calories": 340,
            "protein": 13,
            "carbs": 72,
            "fat": 2.5,
        },
    ),
    RealIngredient(
        name="rye flour",
        category="grain",
        nutrition_per_100g={
            "calories": 325,
            "protein": 16,
            "carbs": 68,
            "fat": 2,
        },
    ),
    RealIngredient(
        name="oats",
        category="grain",
        nutrition_per_100g={
            "calories": 389,
            "protein": 17,
            "carbs": 66,
            "fat": 7,
        },
    ),
    # Sweeteners
    RealIngredient(
        name="honey",
        category="sweetener",
        nutrition_per_100g={
            "calories": 304,
            "protein": 0.3,
            "carbs": 82,
            "fat": 0,
        },
    ),
    RealIngredient(
        name="maple syrup",
        category="sweetener",
        nutrition_per_100g={
            "calories": 260,
            "protein": 0,
            "carbs": 67,
            "fat": 0,
        },
    ),
    # Fats
    RealIngredient(
        name="butter",
        category="dairy",
        nutrition_per_100g={
            "calories": 717,
            "protein": 0.9,
            "carbs": 0.1,
            "fat": 81,
        },
    ),
    RealIngredient(
        name="olive oil",
        category="fat",
        nutrition_per_100g={
            "calories": 884,
            "protein": 0,
            "carbs": 0,
            "fat": 100,
        },
    ),
    RealIngredient(
        name="coconut oil",
        category="fat",
        nutrition_per_100g={
            "calories": 862,
            "protein": 0,
            "carbs": 0,
            "fat": 100,
        },
    ),
    # Dairy
    RealIngredient(
        name="whole milk",
        category="dairy",
        nutrition_per_100g={
            "calories": 61,
            "protein": 3.3,
            "carbs": 4.8,
            "fat": 3.3,
        },
    ),
    RealIngredient(
        name="heavy cream",
        category="dairy",
        nutrition_per_100g={
            "calories": 340,
            "protein": 2.1,
            "carbs": 2.8,
            "fat": 36,
        },
    ),
    RealIngredient(
        name="eggs",
        category="protein",
        nutrition_per_100g={
            "calories": 155,
            "protein": 13,
            "carbs": 1.1,
            "fat": 11,
        },
    ),
    # Leaveners
    RealIngredient(
        name="baking powder",
        category="leavener",
        nutrition_per_100g={
            "calories": 53,
            "protein": 0,
            "carbs": 28,
            "fat": 0,
        },
    ),
    RealIngredient(
        name="baking soda",
        category="leavener",
        nutrition_per_100g={"calories": 0, "protein": 0, "carbs": 0, "fat": 0},
    ),
    RealIngredient(
        name="active dry yeast",
        category="leavener",
        nutrition_per_100g={
            "calories": 325,
            "protein": 40,
            "carbs": 41,
            "fat": 5,
        },
    ),
    # Spices
    RealIngredient(
        name="cinnamon",
        category="spice",
        nutrition_per_100g={
            "calories": 247,
            "protein": 4,
            "carbs": 81,
            "fat": 1.2,
        },
    ),
    RealIngredient(
        name="saffron",
        category="spice",
        nutrition_per_100g={
            "calories": 310,
            "protein": 11,
            "carbs": 65,
            "fat": 5.8,
        },
    ),
    RealIngredient(
        name="turmeric",
        category="spice",
        nutrition_per_100g={
            "calories": 354,
            "protein": 7.8,
            "carbs": 65,
            "fat": 10,
        },
    ),
    RealIngredient(
        name="black pepper",
        category="spice",
        nutrition_per_100g={
            "calories": 251,
            "protein": 10,
            "carbs": 64,
            "fat": 3.3,
        },
    ),
    RealIngredient(
        name="cayenne pepper",
        category="spice",
        nutrition_per_100g={
            "calories": 318,
            "protein": 12,
            "carbs": 57,
            "fat": 17,
        },
    ),
    RealIngredient(
        name="cardamom",
        category="spice",
        nutrition_per_100g={
            "calories": 311,
            "protein": 11,
            "carbs": 68,
            "fat": 6.7,
        },
    ),
    # Herbs
    RealIngredient(
        name="fresh mint",
        category="herb",
        nutrition_per_100g={
            "calories": 70,
            "protein": 3.8,
            "carbs": 15,
            "fat": 0.9,
        },
    ),
    RealIngredient(
        name="fresh thyme",
        category="herb",
        nutrition_per_100g={
            "calories": 101,
            "protein": 5.6,
            "carbs": 24,
            "fat": 1.7,
        },
    ),
    RealIngredient(
        name="elderflower",
        category="herb",
        nutrition_per_100g={
            "calories": 73,
            "protein": 0.7,
            "carbs": 18,
            "fat": 0.5,
        },
    ),
    # Nuts & Seeds
    RealIngredient(
        name="almonds",
        category="nut",
        nutrition_per_100g={
            "calories": 579,
            "protein": 21,
            "carbs": 22,
            "fat": 50,
        },
    ),
    RealIngredient(
        name="walnuts",
        category="nut",
        nutrition_per_100g={
            "calories": 654,
            "protein": 15,
            "carbs": 14,
            "fat": 65,
        },
    ),
    # Fruits
    RealIngredient(
        name="figs (dried)",
        category="fruit",
        nutrition_per_100g={
            "calories": 249,
            "protein": 3.3,
            "carbs": 64,
            "fat": 0.9,
        },
    ),
    RealIngredient(
        name="dates",
        category="fruit",
        nutrition_per_100g={
            "calories": 277,
            "protein": 1.8,
            "carbs": 75,
            "fat": 0.2,
        },
    ),
    # Alcohol bases
    RealIngredient(
        name="vodka",
        category="alcohol",
        nutrition_per_100g={
            "calories": 231,
            "protein": 0,
            "carbs": 0,
            "fat": 0,
        },
    ),
    RealIngredient(
        name="mead",
        category="alcohol",
        nutrition_per_100g={
            "calories": 143,
            "protein": 0.1,
            "carbs": 12,
            "fat": 0,
        },
    ),
    RealIngredient(
        name="dry white wine",
        category="alcohol",
        nutrition_per_100g={
            "calories": 82,
            "protein": 0.1,
            "carbs": 2.6,
            "fat": 0,
        },
    ),
    RealIngredient(
        name="dessert wine",
        category="alcohol",
        nutrition_per_100g={
            "calories": 160,
            "protein": 0.1,
            "carbs": 14,
            "fat": 0,
        },
    ),
    RealIngredient(
        name="absinthe",
        category="alcohol",
        nutrition_per_100g={
            "calories": 274,
            "protein": 0,
            "carbs": 2.8,
            "fat": 0,
        },
    ),
    # Other
    RealIngredient(
        name="blue spirulina",
        category="supplement",
        nutrition_per_100g={
            "calories": 290,
            "protein": 57,
            "carbs": 24,
            "fat": 7.7,
        },
    ),
    RealIngredient(
        name="butterfly pea flower",
        category="herb",
        nutrition_per_100g={"calories": 30, "protein": 1, "carbs": 7, "fat": 0},
    ),
    RealIngredient(
        name="coconut milk",
        category="dairy_alt",
        nutrition_per_100g={
            "calories": 230,
            "protein": 2.3,
            "carbs": 6,
            "fat": 24,
        },
    ),
]


if __name__ == "__main__":
    init_db()
    count = seed_real_ingredients(COMMON_INGREDIENTS)
    print(f"Seeded {count} real ingredients")
