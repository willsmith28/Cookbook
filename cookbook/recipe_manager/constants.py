"""constants for RecipeManger
"""
REQUIRED_INGREDIENT_FIELDS = ("name", "recipe_id")

REQUIRED_RECIPE_FIELDS = (
    "name",
    "description",
    "servings",
    "cook_time",
)

REQUIRED_INGREDIENT_IN_RECIPE_FIELDS = (
    "amount",
    "unit",
    "specifier",
    "ingredient_id",
)

REQUIRED_STEP_FIELDS = (
    "order",
    "instruction",
)
