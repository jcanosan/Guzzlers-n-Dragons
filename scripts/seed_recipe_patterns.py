#!/usr/bin/env python3
"""Seed recipe pattern templates for meal types."""

from src.schemas.domain import RecipePattern
from src.services.database import init_db, seed_recipe_patterns

PATTERNS = [
    RecipePattern(
        meal_type="beverage",
        pattern_json={
            "base_liquid": {
                "required": True,
                "options": [
                    "water",
                    "milk",
                    "juice",
                    "alcohol",
                    "tea",
                    "coffee",
                ],
            },
            "flavor_primary": {"required": True, "type": "fictional_or_real"},
            "flavor_secondary": {"required": False, "max": 3},
            "sweetener": {
                "required": False,
                "options": ["honey", "sugar", "maple", "none"],
            },
            "thickener": {
                "required": False,
                "options": ["none", "gelatin", "cornstarch", "egg"],
            },
            "temperature": {
                "required": True,
                "options": ["hot", "cold", "room"],
            },
            "method": {
                "required": True,
                "options": ["steep", "shake", "stir", "blend", "heat"],
            },
            "garnish": {"required": False},
        },
        example_ingredients=[
            "tea leaves",
            "coffee",
            "cocoa",
            "fruit",
            "herbs",
            "spices",
            "alcohol",
        ],
    ),
    RecipePattern(
        meal_type="bread",
        pattern_json={
            "flour_base": {
                "required": True,
                "options": ["wheat", "rye", "corn", "rice", "mixed"],
            },
            "leavener": {
                "required": True,
                "options": ["yeast", "sourdough", "baking_powder", "none"],
            },
            "liquid": {
                "required": True,
                "options": ["water", "milk", "whey", "beer"],
            },
            "fat": {
                "required": False,
                "options": ["butter", "oil", "lard", "none"],
            },
            "sweetener": {
                "required": False,
                "options": ["honey", "sugar", "molasses", "none"],
            },
            "add_ins": {"required": False, "max": 4},
            "shape": {
                "required": True,
                "options": ["loaf", "flatbread", "rolls", "biscuit"],
            },
            "bake_method": {
                "required": True,
                "options": ["oven", "stone", "pan", "dutch_oven"],
            },
        },
        example_ingredients=[
            "flour",
            "yeast",
            "water",
            "salt",
            "seeds",
            "herbs",
            "cheese",
            "nuts",
        ],
    ),
    RecipePattern(
        meal_type="stew",
        pattern_json={
            "protein": {
                "required": True,
                "options": [
                    "beef",
                    "lamb",
                    "chicken",
                    "beans",
                    "lentils",
                    "fish",
                ],
            },
            "aromatics": {
                "required": True,
                "min": 2,
                "options": ["onion", "garlic", "celery", "carrot", "leek"],
            },
            "liquid": {
                "required": True,
                "options": ["broth", "water", "wine", "beer", "coconut_milk"],
            },
            "vegetables": {"required": True, "min": 1, "max": 5},
            "thickener": {
                "required": False,
                "options": [
                    "flour",
                    "cornstarch",
                    "potato",
                    "reduction",
                    "none",
                ],
            },
            "herbs": {"required": False, "max": 4},
            "spice": {"required": False, "max": 3},
            "cook_method": {
                "required": True,
                "options": ["simmer", "slow_cook", "pressure", "oven"],
            },
        },
        example_ingredients=[
            "meat",
            "root vegetables",
            "legumes",
            "tomatoes",
            "wine",
            "herbs",
            "spices",
        ],
    ),
    RecipePattern(
        meal_type="dessert",
        pattern_json={
            "base": {
                "required": True,
                "options": [
                    "cake",
                    "custard",
                    "fruit",
                    "pastry",
                    "pudding",
                    "cookie",
                ],
            },
            "sweetener": {
                "required": True,
                "options": ["sugar", "honey", "maple", "fruit", "syrup"],
            },
            "fat": {
                "required": True,
                "options": ["butter", "oil", "cream", "egg_yolk", "nut_butter"],
            },
            "flavor_primary": {"required": True},
            "flavor_secondary": {"required": False, "max": 3},
            "texture_element": {
                "required": False,
                "options": ["crunch", "cream", "gel", "crumb", "none"],
            },
            "set_method": {
                "required": True,
                "options": ["bake", "chill", "freeze", "steam", "set"],
            },
            "garnish": {"required": False},
        },
        example_ingredients=[
            "flour",
            "sugar",
            "butter",
            "eggs",
            "cream",
            "chocolate",
            "fruit",
            "nuts",
            "spices",
        ],
    ),
    RecipePattern(
        meal_type="soup",
        pattern_json={
            "base": {
                "required": True,
                "options": ["broth", "cream", "tomato", "pureed_veg", "water"],
            },
            "protein": {
                "required": False,
                "options": [
                    "chicken",
                    "beans",
                    "lentils",
                    "fish",
                    "tofu",
                    "none",
                ],
            },
            "vegetables": {"required": True, "min": 1, "max": 6},
            "aromatics": {"required": True, "min": 1},
            "herbs": {"required": False, "max": 3},
            "spice": {"required": False, "max": 2},
            "finish": {
                "required": False,
                "options": ["cream", "herbs", "oil", "acid", "cheese", "none"],
            },
            "texture": {
                "required": True,
                "options": ["chunky", "pureed", "clear", "thickened"],
            },
        },
        example_ingredients=[
            "stock",
            "vegetables",
            "legumes",
            "pasta",
            "rice",
            "herbs",
            "cream",
        ],
    ),
    RecipePattern(
        meal_type="preserve",
        pattern_json={
            "primary_ingredient": {
                "required": True,
                "options": ["fruit", "vegetable", "herb", "meat", "fish"],
            },
            "method": {
                "required": True,
                "options": [
                    "jam",
                    "pickle",
                    "ferment",
                    "cure",
                    "dry",
                    "confit",
                    "syrup",
                ],
            },
            "acid": {
                "required": False,
                "options": ["vinegar", "lemon", "whey", "none"],
            },
            "salt": {"required": True, "type": "ratio"},
            "sweetener": {
                "required": False,
                "options": ["sugar", "honey", "maple", "none"],
            },
            "spice": {"required": False, "max": 4},
            "herb": {"required": False, "max": 3},
            "storage": {
                "required": True,
                "options": ["jar", "crock", "vacuum", "dry", "oil"],
            },
        },
        example_ingredients=[
            "fruit",
            "vinegar",
            "salt",
            "sugar",
            "spices",
            "herbs",
            "oil",
        ],
    ),
    RecipePattern(
        meal_type="sauce",
        pattern_json={
            "base": {
                "required": True,
                "options": [
                    "roux",
                    "reduction",
                    "emulsion",
                    "puree",
                    "broth",
                    "cream",
                ],
            },
            "fat": {
                "required": False,
                "options": ["butter", "oil", "rendered_fat", "none"],
            },
            "flavor_base": {
                "required": True,
                "options": ["aromatics", "stock", "wine", "tomato", "fruit"],
            },
            "thickener": {
                "required": False,
                "options": [
                    "flour",
                    "cornstarch",
                    "reduction",
                    "egg_yolk",
                    "puree",
                    "none",
                ],
            },
            "seasoning": {"required": True, "max": 5},
            "finish": {
                "required": False,
                "options": [
                    "butter",
                    "cream",
                    "herbs",
                    "acid",
                    "cheese",
                    "none",
                ],
            },
            "method": {
                "required": True,
                "options": ["whisk", "blend", "reduce", "emulsify", "simmer"],
            },
        },
        example_ingredients=[
            "butter",
            "flour",
            "stock",
            "wine",
            "cream",
            "herbs",
            "tomato",
            "mustard",
        ],
    ),
]


if __name__ == "__main__":
    init_db()
    count = seed_recipe_patterns(PATTERNS)
    print(f"Seeded {count} recipe patterns")
