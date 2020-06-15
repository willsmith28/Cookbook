# from sqlalchemy.sql.expression import exists, func
# from .database import db

# ###############
# # Query helpers
# ###############
# async def _recipe_exists(database: databases.Database, recipe_id: int) -> bool:
#     query = exists(db.recipes.select().where(db.recipes.c.id == recipe_id)).select()
#     return await database.execute(query)


# async def _ingredient_in_recipe_exists(
#     database: databases.Database, recipe_id: int, ingredient_id: int
# ) -> bool:
#     query = exists(
#         db.ingredients_in_recipe.select().where(
#             db.ingredients_in_recipe.c.recipe_id == recipe_id,
#             db.ingredients_in_recipe.c.ingredient_id == ingredient_id,
#         )
#     ).select()
#     return await database.execute(query)


# async def _tag_exists(database: databases.Database, tag_id: int) -> bool:
#     query = exists(db.tags.select().where(db.tags.c.id == tag_id)).select()
#     return await database.execute(query)


# async def _step_in_recipe_exists(
#     database: databases.Database, recipe_id: int, order: int
# ) -> bool:
#     query = exists(
#         db.steps.select().where(
#             db.steps.c.recipe_id == recipe_id, db.steps.c.order == order
#         )
#     ).select()
#     return await database.execute(query)


# async def _step_count(database: databases.Database, recipe_id: int) -> int:
#     step_count_query = (
#         db.steps.select()
#         .where(db.steps.c.recipe_id == recipe_id)
#         .with_only_columns([func.count()])
#     )
#     return await database.execute(step_count_query)
