from typing import List, Union
from asyncpg.exceptions import IntegrityConstraintViolationError
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from ..serializers import Ingredient, IngredientCreate, ErrorMessage
from ..constants import INGREDIENT_UNITS
from .. import models, utils

NOT_FOUND_RESPONSE = {"message": "Ingredient not found."}

router = APIRouter()

##############
# /ingredients
##############
@router.get("/", tags=["ingredients"], response_model=List[Ingredient])
async def get_ingredients():
    """Get list of ingredients

    Returns:
        tuple[dict]: collection of ingredients
    """
    ingredients = await models.Ingredient.query.gino.all()
    return tuple(ingredient.to_dict() for ingredient in ingredients)


@router.post(
    "/",
    tags=["ingredients"],
    response_model=Ingredient,
    responses={422: {"model": ErrorMessage}},
    status_code=201,
)
async def create_ingredient(ingredient: IngredientCreate):
    try:
        created_ingredient = await models.Ingredient.create(**ingredient.dict())

    except IntegrityConstraintViolationError as error:
        response = JSONResponse(status_code=422, content={"message": str(error)})

    else:
        response = created_ingredient.to_dict()

    return response


###################################
# /ingredients/{ingredient_id: int}
###################################
@router.get(
    "/{ingredient_id}",
    tags=["ingredients"],
    response_model=Ingredient,
    responses={404: {"model": ErrorMessage}},
)
async def get_ingredient_detail(ingredient_id: str):
    ingredient = await models.Ingredient.get(ingredient_id)
    return (
        ingredient.to_dict()
        if ingredient
        else JSONResponse(status_code=404, content=NOT_FOUND_RESPONSE)
    )


@router.put(
    "/{ingredient_id}",
    tags=["ingredients"],
    response_model=Ingredient,
    responses={404: {"model": ErrorMessage}, 422: {"model": ErrorMessage}},
)
async def edit_ingredient(ingredient_id: str, ingredient: IngredientCreate):
    if not (db_ingredient := await models.Ingredient.get(ingredient_id)):
        return JSONResponse(status_code=404, content=NOT_FOUND_RESPONSE)

    try:
        await db_ingredient.update(**ingredient.dict()).apply()

    except IntegrityConstraintViolationError as error:
        response = JSONResponse(status_code=422, content={"message": error.__cause__})

    else:
        response = db_ingredient.to_dict()

    return response


####################
# /ingredients/units
####################
@router.get(
    "/units", tags=["ingredients"], response_model=List[Union[str, List[List[str]]]]
)
def get_ingredient_units():
    return INGREDIENT_UNITS
