"""
Defines db tables and connection
"""
import datetime
import os
import databases
import sqlalchemy
from sqlalchemy.sql import func

USER = os.environ.get("SQL_USER", "user")
PASSWORD = os.environ.get("SQL_PASSWORD", "password")
HOST = os.environ.get("SQL_HOST", "localhost")
PORT = os.environ.get("SQL_PORT", "5432")
DB = os.environ.get("SQL_DATABASE", "")

DATABASE_URL = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}"

metadata = sqlalchemy.MetaData()


async def get_database_connection() -> databases.Database:
    """gets connection to database

    Returns:
        databases.Database: connected db connection

    Yields:
        Iterator[databases.Database]: [description]
    """
    async with databases.Database(DATABASE_URL) as database:
        async with database.transaction():
            yield database


ingredients = sqlalchemy.Table(
    "ingredients",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.INTEGER, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String, nullable=False, unique=True),
    sqlalchemy.Column(
        "recipe_id",
        sqlalchemy.ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=True,
        unique=True,
    ),
)

tags = sqlalchemy.Table(
    "tags",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.INTEGER, primary_key=True),
    sqlalchemy.Column("value", sqlalchemy.String, nullable=False, unique=True),
    sqlalchemy.Column("kind", sqlalchemy.String, nullable=False),
)

recipes = sqlalchemy.Table(
    "recipes",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.INTEGER, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String, nullable=False, unique=True),
    sqlalchemy.Column("description", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("servings", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("cook_time", sqlalchemy.String, nullable=False),
    sqlalchemy.Column(
        "created_on", sqlalchemy.DateTime, server_default=func.now(), nullable=False
    ),
    sqlalchemy.Column("last_updated_on", sqlalchemy.DateTime, onupdate=func.now()),
)

ingredients_in_recipe = sqlalchemy.Table(
    "ingredients_in_recipe",
    metadata,
    sqlalchemy.Column(
        "amount", sqlalchemy.DECIMAL(precision=6, scale=2), nullable=False
    ),
    sqlalchemy.Column("unit", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("specifier", sqlalchemy.String, nullable=False),
    sqlalchemy.Column(
        "recipe_id",
        sqlalchemy.ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=False,
    ),
    sqlalchemy.Column(
        "ingredient_id",
        metadata,
        sqlalchemy.ForeignKey("ingredients.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sqlalchemy.PrimaryKeyConstraint(
        "recipe_id", "ingredient_id", name="ingredient_in_recipe_primary_key"
    ),
)

recipe_tags = sqlalchemy.Table(
    "recipe_tags",
    metadata,
    sqlalchemy.Column(
        "recipe_id", sqlalchemy.ForeignKey("recipes.id", ondelete="CASCADE")
    ),
    sqlalchemy.Column("tag_id", sqlalchemy.ForeignKey("tags.id", ondelete="CASCADE")),
    sqlalchemy.PrimaryKeyConstraint(
        "recipe_id", "tag_id", name="recipe_tag_primary_key"
    ),
)

steps = sqlalchemy.Table(
    "steps",
    metadata,
    sqlalchemy.Column("order", sqlalchemy.INTEGER),
    sqlalchemy.Column("instruction", sqlalchemy.String),
    sqlalchemy.Column(
        "recipe_id",
        sqlalchemy.ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=False,
    ),
    sqlalchemy.PrimaryKeyConstraint("order", "recipe_id", name="step_primary_key"),
)
