from typing import List
from fastapi import APIRouter
from ..models.db import database, ingredients
from ..models.serializers import Ingredient, IngredientCreate

router = APIRouter()


@router.get("/", tags=["ingredients"], response_model=List[Ingredient])
async def get_ingredients():
    query = ingredients.select()
    return await database.fetch_all(query)


@router.post("/", tags=["ingredients"], response_model=Ingredient)
async def create_ingredient(ingredient: IngredientCreate):
    query = ingredients.insert().values(
        name=ingredient.name, recipe_id=ingredient.recipe_id
    )
    created_ingredient_id = await database.execute(query)
    return {**ingredient.dict(), "id": created_ingredient_id}


@router.get("/{ingredient_id}", tags=["ingredients"], response_model=Ingredient)
async def get_ingredient_detail(ingredient_id: int):
    return await ingredients.select().where(ingredients.c.id == ingredient_id)
