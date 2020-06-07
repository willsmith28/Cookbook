from typing import List, Union

from sqlite3 import IntegrityError
from sqlalchemy.sql.expression import exists

from asyncpg.exceptions import IntegrityConstraintViolationError
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
import databases
from ..models.serializers import Ingredient, IngredientCreate, ErrorMessage
from ..models import db
from ..constants import INGREDIENT_UNITS

NOT_FOUND_RESPONSE = {"message": "Ingredient not found."}

router = APIRouter()

##############
# /ingredients
##############
@router.get("/", tags=["ingredients"], response_model=List[Ingredient])
async def get_ingredients(
    database: databases.Database = Depends(db.get_database_connection),
):
    query = db.ingredients.select()
    return await database.fetch_all(query)


@router.post(
    "/",
    tags=["ingredients"],
    response_model=Ingredient,
    responses={422: {"model": ErrorMessage}},
    status_code=201,
)
async def create_ingredient(
    ingredient: IngredientCreate,
    database: databases.Database = Depends(db.get_database_connection),
):
    query = db.ingredients.insert().values(**ingredient.dict())
    try:
        created_ingredient_id = await database.execute(query)

    except (IntegrityError, IntegrityConstraintViolationError) as error:
        return JSONResponse(status_code=422, content={"message": error.__cause__})

    return {**ingredient.dict(), "id": created_ingredient_id}


###################################
# /ingredients/{ingredient_id: int}
###################################
@router.get(
    "/{ingredient_id}",
    tags=["ingredients"],
    response_model=Ingredient,
    responses={404: {"model": ErrorMessage}},
)
async def get_ingredient_detail(
    ingredient_id: int,
    database: databases.Database = Depends(db.get_database_connection),
):
    query = db.ingredients.select().where(db.ingredients.c.id == ingredient_id)
    ingredient = await database.fetch_one(query)

    return (
        ingredient
        if ingredient
        else JSONResponse(status_code=404, content=NOT_FOUND_RESPONSE)
    )


@router.put(
    "/{ingredient_id}",
    tags=["ingredients"],
    response_model=Ingredient,
    responses={404: {"model": ErrorMessage}, 422: {"model": ErrorMessage}},
)
async def edit_ingredient(
    ingredient_id: int,
    ingredient: IngredientCreate,
    database: databases.Database = Depends(db.get_database_connection),
):
    query = exists(
        db.ingredients.select().where(db.ingredients.c.id == ingredient_id)
    ).select()
    ingredient_exists = await database.execute(query)
    if not ingredient_exists:
        return JSONResponse(status_code=404, content=NOT_FOUND_RESPONSE)

    query = (
        db.ingredients.update()
        .values(**ingredient.dict())
        .where(db.ingredients.c.id == ingredient_id)
    )
    try:
        await database.execute(query)
    except (IntegrityError, IntegrityConstraintViolationError) as error:
        return JSONResponse(status_code=422, content={"message": error.__cause__})

    return {**ingredient.dict(), "id": ingredient_id}


####################
# /ingredients/units
####################
@router.get(
    "/units", tags=["ingredients"], response_model=List[Union[str, List[List[str]]]]
)
def get_ingredient_units():
    return INGREDIENT_UNITS
