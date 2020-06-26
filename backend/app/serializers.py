"""
serializer models
"""
from typing import Optional, List, Union
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, validator


def positive_number(value: int) -> int:
    """validate value is positive
    Args:
        value (int): value to test

    Raises:
        ValueError: if value is negative

    Returns:
        int: value
    """
    if value <= 0:
        raise ValueError("servings must be positive")

    return value


class ErrorMessage(BaseModel):
    message: str


class ErrorMessageDetail(BaseModel):
    loc: List[str]
    msg: str
    type: str


class UnprocessableErrorMessage(BaseModel):
    detail: List[ErrorMessageDetail]
    body: dict


class Ingredient(BaseModel):
    id: UUID
    name: str
    recipe_id: Optional[UUID]


class IngredientCreate(BaseModel):
    name: str
    recipe_id: Optional[UUID] = None


class Tag(BaseModel):
    id: UUID
    value: str
    kind: str


class TagCreate(BaseModel):
    value: str
    kind: str


class AddTagToRecipe(BaseModel):
    id: UUID


class IngredientInRecipe(BaseModel):
    amount: Union[int, float, Decimal]
    unit: str
    specifier: str
    ingredient_id: UUID

    _positive_amount = validator("amount", allow_reuse=True)(positive_number)


class StepCreateResponse(BaseModel):
    order: int
    instruction: str


class Step(BaseModel):
    instruction: str


class Recipe(BaseModel):
    id: UUID
    name: str
    description: str
    servings: int
    cook_time: str
    created_on: datetime
    last_updated_on: datetime


class RecipeWithRelations(BaseModel):
    id: UUID
    name: str
    description: str
    servings: int
    cook_time: str
    created_on: datetime
    last_updated_on: datetime

    ingredients: List[IngredientInRecipe]
    steps: List[str]
    tags: List[UUID]


class RecipeCreate(BaseModel):
    name: str
    description: str
    servings: int
    cook_time: str

    _positive_servings = validator("servings", allow_reuse=True)(positive_number)
