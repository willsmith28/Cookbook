from sqlalchemy.sql.expression import func
from . import models

###############
# Query helpers
###############
async def recipe_exists(recipe_id: int) -> bool:
    return await models.db.scalar(
        models.db.exists().where(models.Recipes.id == recipe_id).select()
    )


async def ingredient_in_recipe_exists(recipe_id: int, ingredient_id: int) -> bool:
    return await models.db.scalar(
        models.db.exists()
        .where(
            models.IngredientInRecipe.recipe_id == recipe_id,
            models.IngredientInRecipe.ingredient_id == ingredient_id,
        )
        .select()
    )


async def tag_exists(tag_id: int) -> bool:
    return await models.db.scalar(models.db.exists().where(models.Tags.id == tag_id))


async def ingredient_exists(ingredient_id: int) -> bool:
    return await models.db.scalar(
        models.db.exists().where(models.Ingredient.id == ingredient_id)
    )


async def step_in_recipe_exists(recipe_id: int, order: int) -> bool:
    return await models.db.scalar(
        models.db.exists()
        .where(models.Step.recipe_id == recipe_id, models.Step.order == order)
        .select()
    )


async def step_count(recipe_id: int) -> int:
    step_count_query = models.db.func.count(models.Step.id)
    return await models.db.scalar(
        models.db.select([step_count_query]).where(models.Step.recipe_id == recipe_id)
    )

