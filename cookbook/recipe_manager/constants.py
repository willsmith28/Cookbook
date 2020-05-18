"""constants for RecipeManger
"""
from rest_framework import response, status

REQUIRED_INGREDIENT_FIELDS = ("name", "recipe_id")

REQUIRED_TAG_FIELDS = ("value", "kind")

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

REQUIRED_MEAL_PLAN_FIELDS = ("recipe_id", "planned_date")

NOT_ALLOWED_RESPONSE = response.Response(
    {
        "errors": {
            "non_field_errors": (
                "You cannot make changes to a recipe you are not the author of.",
            )
        }
    },
    status=status.HTTP_403_FORBIDDEN,
)
