from typing import Dict, List
import os
import pathlib
import json
import functools
import pytest
import sqlalchemy
import databases
from ..app.models import db

TEST_DATABASE_URL = "sqlite:///db.sqlite3"


async def override_get_db_connection():
    async with databases.Database(TEST_DATABASE_URL, force_rollback=True) as database:
        async with database.transaction():
            yield database


@pytest.fixture(scope="session")
def test_db():
    # setup test db
    engine = sqlalchemy.create_engine(
        TEST_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    db.metadata.create_all(engine)
    with engine.connect() as connection:
        yield connection

    # cleanup

    engine.dispose()
    os.remove(pathlib.Path("./db.sqlite3"))


def load_test_data(connection, json_filename: str):
    # load test data
    cwd = pathlib.Path.cwd()
    json_path = pathlib.Path(f"app/models/fixtures/{json_filename}")
    with open(cwd / json_path) as json_fixtures:
        fixtures = json.load(json_fixtures)

    for data in fixtures:
        model = _MODELS[data["model"]]
        query = model.insert().values(**data["fields"])
        connection.execute(query)


def load_and_rollback_test_data(json_filename):
    def decorator_load_and_rollback(func):
        @functools.wraps(func)
        def wrapper(test_db):
            # load test data
            cwd = pathlib.Path.cwd()
            json_path = pathlib.Path(f"app/models/fixtures/{json_filename}")
            with open(cwd / json_path) as json_fixtures:
                fixtures = json.load(json_fixtures)

            for data in fixtures:
                model = _MODELS[data["model"]]
                query = model.insert().values(**data["fields"])
                test_db.execute(query)

            try:
                func(test_db)
            finally:
                for table in _MODELS.values():
                    test_db.execute(table.delete())

        return wrapper

    return decorator_load_and_rollback


def rollback_test_data(func):
    @functools.wraps(func)
    def wrapper(test_db):
        func(test_db)

        for table in _MODELS.values():
            test_db.execute(table.delete())

    return wrapper


_MODELS = {
    "ingredient": db.ingredients,
    "recipe": db.recipes,
    "ingredient_in_recipe": db.ingredients_in_recipe,
    "tag": db.tags,
    "recipe_tag": db.recipe_tags,
    "step": db.steps,
}
