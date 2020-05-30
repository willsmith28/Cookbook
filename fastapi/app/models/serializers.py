from typing import Optional, List, Union
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, validator


def positive_number(value: int) -> int:
    if value <= 0:
        raise ValueError("servings must be positive")

    return value


class Ingredient(BaseModel):
    id: int
    name: str
    recipe_id: Optional[int]


class Tag(BaseModel):
    id: int
    value: str
    kind: str


class IngredientInRecipe(BaseModel):
    amount: Decimal
    unit: str
    specifier: str
    ingredient_id: int
    recipe_id: int


class Step(BaseModel):
    order: int
    instruction: str
    recipe_id: int


class Recipe(BaseModel):
    id: int
    name: str
    description: str
    servings: int
    cook_time: str
    created_on: datetime
    last_updated_on: datetime

    ingredients: List[IngredientInRecipe]
    steps: List[str]
    tags: List[int]


class IngredientCreate(BaseModel):
    name: str
    recipe_id: Optional[int] = None


class RecipeCreate(BaseModel):
    name: str
    description: str
    servings: int
    cook_time: str

    _positive_servings = validator("servings", allow_reuse=True)(positive_number)


class StepCreate(BaseModel):
    instruction: str


class IngredientInRecipeCreate(BaseModel):
    amount: Decimal
    unit: str
    specifier: str
    ingredient_id: int

    _positive_amount = validator("amount", allow_reuse=True)(positive_number)
