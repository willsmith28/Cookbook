"""
Defines db tables and connection
"""
from gino.ext.starlette import Gino
from sqlalchemy.sql import func
from . import config

db = Gino(
    dsn=config.DB_DSN,
    pool_min_size=config.DB_POOL_MIN_SIZE,
    pool_max_size=config.DB_POOL_MAX_SIZE,
    echo=config.DB_ECHO,
    ssl=config.DB_SSL,
    use_connection_for_request=config.DB_USE_CONNECTION_FOR_REQUEST,
    retry_limit=config.DB_RETRY_LIMIT,
    retry_interval=config.DB_RETRY_INTERVAL,
)


class Ingredients(db.Model):
    __tablename__ = "ingredients"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    recipe_id = db.Column(db.ForeignKey("recipes.id", ondelete="CASCADE"), unique=True)


class Tags(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String, nullable=False, unique=True)
    kind = db.Column(db.String, nullable=False)


class Recipes(db.Model):
    __tablename__ = "recipes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.String, nullable=False)
    servings = db.Column(db.Integer, nullable=False)
    cook_time = db.Column(db.String, nullable=False)
    created_on = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    last_updated_on = db.Column(db.DateTime, onupdate=func.now())


class IngredientInRecipe(db.Model):
    __tablename__ = "ingredients_in_recipe"
    _pk = db.PrimaryKeyConstraint(
        "recipe_id", "ingredient_id", name="ingredients_in_recipe_pk"
    )
    amount = db.Column(db.DECIMAL(precision=6, scale=2), nullable=False)
    unit = db.Column(db.String, nullable=False)
    specifier = db.Column(db.String, nullable=False)
    recipe_id = db.Column(
        db.ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False,
    )
    ingredient_id = db.Column(
        db.ForeignKey("ingredients.id", ondelete="RESTRICT"), nullable=False,
    )


class RecipeTags(db.Model):
    __tablename__ = "recipe_tags"
    _pk = db.PrimaryKeyConstraint("recipe_id", "tag_id", name="recipe_tag_primary_key")
    recipe_id = db.Column(db.ForeignKey("recipes.id", ondelete="CASCADE"))
    tag_id = db.Column(db.ForeignKey("tags.id", ondelete="CASCADE"))


class Step(db.Model):
    __tablename__ = "steps"
    _pk = db.PrimaryKeyConstraint("order", "recipe_id", name="step_primary_key")
    order = db.Column(db.INTEGER)
    instruction = db.Column(db.String)
    recipe_id = db.Column(
        db.ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False,
    )
