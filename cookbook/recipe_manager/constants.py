"""constants for RecipeManger
"""
from rest_framework import response, status

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

NOT_ALLOWED_RESPONSE = response.Response(
    {"message": "Cannot edit a recipe that is not yours"},
    status=status.HTTP_403_FORBIDDEN,
)
