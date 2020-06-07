"""
Recipe routes
"""
from typing import List
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response
import databases
from ..models.serializers import (
    Recipe,
    RecipeCreate,
    IngredientInRecipe,
    Step,
    StepCreateResponse,
    AddTagToRecipe,
    ErrorMessage,
)
from ..models import db
from .. import utils

RECIPE_NOT_FOUND = {"message": "Recipe not found"}
INGREDIENT_IN_RECIPE_NOT_FOUND = {"message": "Ingredient not found for that recipe"}
STEP_NOT_FOUND = {"message": "Step not found for that recipe"}

router = APIRouter()


##########
# recipes
# /recipes
##########


@router.get("/", tags=["recipes"], response_model=List[Recipe])
async def get_recipes(
    database: databases.Database = Depends(db.get_database_connection),
):
    """Get list of recipes"""
    query = db.recipes.select()
    return await database.fetch_all(query)


@router.post(
    "/", tags=["recipes"], response_model=Recipe, status_code=201,
)
async def create_recipe(
    recipe: RecipeCreate,
    database: databases.Database = Depends(db.get_database_connection),
):
    """Add new recipe"""
    query = db.recipes.insert().values(**recipe.dict())
    # TODO catch integrity error
    created_recipe_id = await database.execute(query)
    return {**recipe.dict(), "id": created_recipe_id}


###########################
# recipe detail
# /recipes/{recipe_id: int}
###########################


@router.get(
    "/{recipe_id}",
    tags=["recipes"],
    response_model=Recipe,
    responses={404: {"model": ErrorMessage}},
)
async def get_recipe_detail(
    recipe_id: int, database: databases.Database = Depends(db.get_database_connection)
):
    """Gets recipe detail"""
    query = db.recipes.select().where(db.recipes.c.id == recipe_id)
    recipe = await database.fetch_one(query)

    return recipe if recipe else JSONResponse(status_code=404, content=RECIPE_NOT_FOUND)


@router.put(
    "/{recipe_id}",
    tags=["recipes"],
    response_model=Recipe,
    responses={404: {"model": ErrorMessage}},
)
async def edit_recipe(
    recipe_id: int,
    recipe: RecipeCreate,
    database: databases.Database = Depends(db.get_database_connection),
):
    """Edit recipe"""
    recipe_exists = await utils.recipe_exists(database, recipe_id)
    if not recipe_exists:
        return JSONResponse(status_code=404, content=RECIPE_NOT_FOUND)

    query = (
        db.recipes.update().values(**recipe.dict()).where(db.recipes.c.id == recipe_id)
    )
    # TODO catch integrity error
    await database.execute(query)

    return {**recipe.dict(), "id": recipe_id}


#######################################
# ingredients in recipe
# /recipes/{recipe_id: int}/ingredients
#######################################


@router.get(
    "/recipes/{recipe_id}/ingredients",
    tags=["recipes"],
    response_model=List[IngredientInRecipe],
    responses={404: {"model": ErrorMessage}},
)
async def get_ingredients_in_recipe(
    recipe_id: int, database: databases.Database = Depends(db.get_database_connection),
):
    recipe_exists = await utils.recipe_exists(database, recipe_id)
    if not recipe_exists:
        return JSONResponse(status_code=404, content=RECIPE_NOT_FOUND)

    query = (
        db.ingredients_in_recipe.select()
        .with_only_columns(
            [
                db.ingredients_in_recipe.c.amount,
                db.ingredients_in_recipe.c.unit,
                db.ingredients_in_recipe.c.specifier,
                db.ingredients_in_recipe.c.ingredient_id,
            ]
        )
        .where(db.ingredients_in_recipe.c.recipe_id == recipe_id)
    )

    return await database.fetch_all(query)


@router.post(
    "/recipes/{recipe_id}/ingredients",
    tags=["recipes"],
    response_model=List[IngredientInRecipe],
    responses={404: {"model": ErrorMessage}},
    status_code=201,
)
async def add_ingredient_to_recipe(
    recipe_id: int,
    ingredient_in_recipe: IngredientInRecipe,
    database: databases.Database = Depends(db.get_database_connection),
):
    recipe_exists = await utils.recipe_exists(database, recipe_id)
    if not recipe_exists:
        return JSONResponse(status_code=404, content=RECIPE_NOT_FOUND)

    query = db.ingredients_in_recipe.insert().values(
        recipe_id=recipe_id, **ingredient_in_recipe.dict()
    )
    # TODO catch integrity error
    await database.execute(query)
    return ingredient_in_recipe.dict()


############################################################
# ingredient in recipe detail
# /recipes/{recipe_id: int}/ingredients/{ingredient_id: int}
############################################################


@router.get(
    "/recipes/{recipe_id}/ingredients/{ingredient_id}",
    tags=["recipes"],
    response_model=IngredientInRecipe,
    responses={404: {"model": ErrorMessage}},
)
async def get_ingredient_in_recipe_detail(
    recipe_id: int,
    ingredient_id: int,
    database: databases.Database = Depends(db.get_database_connection),
):
    query = (
        db.ingredients_in_recipe.select()
        .with_only_columns(
            [
                db.ingredients_in_recipe.c.amount,
                db.ingredients_in_recipe.c.unit,
                db.ingredients_in_recipe.c.specifier,
                db.ingredients_in_recipe.c.ingredient_id,
            ]
        )
        .where(
            db.ingredients_in_recipe.c.recipe_id == recipe_id,
            db.ingredients_in_recipe.c.ingedient_id == ingredient_id,
        )
    )
    ingredient_in_recipe = await database.fetch_one(query)

    return (
        ingredient_in_recipe
        if ingredient_in_recipe
        else JSONResponse(
            status_code=404, content={"message": "Ingredient or recipe not found"}
        )
    )


@router.put(
    "/recipes/{recipe_id}/ingredients/{ingredient_id}",
    tags=["recipes"],
    response_model=IngredientInRecipe,
    responses={404: {"model": ErrorMessage}},
)
async def edit_ingredient_in_recipe(
    recipe_id: int,
    ingredient_id: int,
    ingredient_in_recipe: IngredientInRecipe,
    database: databases.Database = Depends(db.get_database_connection),
):
    ingredient_exists = await utils.ingredient_in_recipe_exists(
        database, recipe_id, ingredient_id
    )
    if not ingredient_exists:
        return JSONResponse(status_code=404, content=RECIPE_NOT_FOUND)

    query = (
        db.ingredients_in_recipe.update()
        .values(recipe_id=recipe_id, **ingredient_in_recipe.dict())
        .where(
            db.ingredients_in_recipe.c.recipe_id == recipe_id,
            db.ingredients_in_recipe.c.ingredient_id == ingredient_id,
        )
    )
    await database.execute(query)
    return ingredient_in_recipe.dict()


@router.delete(
    "/recipes/{recipe_id}/ingredients/{ingredient_id}",
    tags=["recipes"],
    responses={404: {"model": ErrorMessage}},
    status_code=204,
)
async def remove_ingredient_from_recipe(
    recipe_id: int,
    ingredient_id: int,
    database: databases.Database = Depends(db.get_database_connection),
):
    ingredient_exists = await utils.ingredient_in_recipe_exists(
        database, recipe_id, ingredient_id
    )
    if not ingredient_exists:
        return JSONResponse(status_code=404, content=INGREDIENT_IN_RECIPE_NOT_FOUND)

    query = db.ingredients_in_recipe.delete().where(
        db.ingredients_in_recipe.c.recipe_id == recipe_id,
        db.ingredients_in_recipe.c.ingredient_id,
    )
    await database.execute(query)
    return Response(status_code=204)


#########################
# recipe steps
# /{recipe_id: int}/steps
#########################


@router.get(
    "/{recipe_id}/steps",
    tags=["recipes"],
    response_model=List[str],
    responses={404: {"model": ErrorMessage}},
)
async def get_recipe_steps(
    recipe_id: int, database: databases.Database = Depends(db.get_database_connection),
):
    recipe_exists = await utils.recipe_exists(database, recipe_id)
    if not recipe_exists:
        return JSONResponse(status_code=404, content=RECIPE_NOT_FOUND)

    query = (
        db.steps.select()
        .with_only_columns([db.steps.c.instruction])
        .where(db.steps.c.recipe_id == recipe_id)
        .order_by(db.steps.c.order)
    )
    steps = await database.fetch_all(query)
    return tuple(step[db.steps.c.instruction] for step in steps)


@router.post(
    "/{recipe_id}/steps",
    tags=["recipes"],
    response_model=StepCreateResponse,
    responses={404: {"model": ErrorMessage}},
    status_code=201,
)
async def add_step_to_recipe(
    recipe_id: int,
    step: Step,
    database: databases.Database = Depends(db.get_database_connection),
):
    recipe_exists = await utils.recipe_exists(database, recipe_id)
    if not recipe_exists:
        return JSONResponse(status_code=404, content=RECIPE_NOT_FOUND)

    step_count = await utils.step_count(database, recipe_id)
    order = step_count + 1
    query = db.steps.insert().values(
        recipe_id=recipe_id, instruction=step.instruction, order=order
    )
    await database.execute(query)
    return {**step.dict(), "order": order}


######################################
# recipe step detail
# /{recipe_id: int}/steps/{order: int}
######################################


@router.get(
    "/{recipe_id}/steps/{order}",
    tags=["recipes"],
    response_model=Step,
    responses={404: {"model": ErrorMessage}},
)
async def get_step_detail(
    recipe_id: int,
    order: int,
    database: databases.Database = Depends(db.get_database_connection),
):
    query = db.steps.select().where(
        db.steps.c.recipe_id == recipe_id, db.steps.c.order == order
    )
    step = await database.fetch_one(query)

    return (
        {"instruction": step[db.steps.c.instruction]}
        if step
        else JSONResponse(status_code=404, content=STEP_NOT_FOUND)
    )


@router.put(
    "/{recipe_id}/steps/{order}",
    tags=["recipes"],
    response_model=Step,
    responses={404: {"model": ErrorMessage}},
)
async def edit_step(
    recipe_id: int,
    order: int,
    step: Step,
    database: databases.Database = Depends(db.get_database_connection),
):
    step_exists = await utils.step_in_recipe_exists(database, recipe_id, order)
    if not step_exists:
        return JSONResponse(status_code=404, content=STEP_NOT_FOUND)

    query = (
        db.steps.update()
        .values(instruction=step.instruction)
        .where(db.steps.c.recipe_id == recipe_id, db.steps.c.order == order)
    )
    await database.execute(query)
    return step.dict()


@router.delete(
    "/{recipe_id}/steps/{order}",
    tags=["recipes"],
    responses={404: {"model": ErrorMessage}},
    status_code=204,
)
async def delete_step(
    recipe_id: int,
    order: int,
    database: databases.Database = Depends(db.get_database_connection),
):
    query = db.steps.select().where(
        db.steps.c.recipe_id == recipe_id, db.steps.c.order == order
    )
    step = await database.fetch_one(query)
    if not step:
        return JSONResponse(status_code=404, content=STEP_NOT_FOUND)

    step_count = await utils.step_count(database, recipe_id)
    if step[db.steps.c.order] == step_count:
        query = db.steps.delete().where(
            db.steps.c.recipe_id == recipe_id, db.steps.c.order == order
        )
        await database.execute(query)
        return Response(status_code=204)

    return JSONResponse(
        status_code=409,
        content={
            "message": f"Only the last step in the recipe can be deleted. Delete step at order: {step_count}"
        },
    )


########################
# recipe tags
# /{recipe_id: int}/tags
########################


@router.post(
    "/{recipe_id}/tags",
    tags=["recipes"],
    responses={404: {"model": ErrorMessage}},
    status_code=201,
)
async def add_tag_to_recipe(
    recipe_id: int,
    tag: AddTagToRecipe,
    database: databases.Database = Depends(db.get_database_connection),
):
    recipe_exists = await utils.recipe_exists(database, recipe_id)
    if not recipe_exists:
        return JSONResponse(status_code=404, content=RECIPE_NOT_FOUND)

    query = db.tags.select().where(db.tags.c.id == tag.id)
    tag = await database.fetch_one(query)

    if not tag:
        return JSONResponse(
            status_code=422, content={"message": "No tag exists with provided id"}
        )
    query = db.recipe_tags.insert().values(recipe_id=recipe_id, tag_id=tag.id)
    await database.execute(query)
    return tag


#################################
# recipe tag detail
# /{recipe_id: int}/tags/{tag_id}
#################################


@router.delete(
    "/{recipe_id}/tags",
    tags=["recipes"],
    responses={404: {"model": ErrorMessage}},
    status_code=204,
)
async def remove_tag_from_recipe(
    recipe_id: int,
    tag_id: int,
    database: databases.Database = Depends(db.get_database_connection),
):
    recipe_exists = await utils.recipe_exists(database, recipe_id)
    if not recipe_exists:
        return JSONResponse(status_code=404, content=RECIPE_NOT_FOUND)
    tag_exists = await utils.tag_exists(database, tag_id)
    if tag_exists:
        return JSONResponse(status_code=404, content={"message": "No tag found"})
    query = db.recipe_tags.delete().where(
        db.recipe_tags.c.recipe_id == recipe_id, db.recipe_tags.c.tag_id == tag_id
    )
    await database.execute(query)
    return Response(status_code=204)
