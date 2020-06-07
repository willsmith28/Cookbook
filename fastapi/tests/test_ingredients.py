"""
Test for /ingredients/
"""
from fastapi.testclient import TestClient
import sqlalchemy
import pytest
from .db import (
    TEST_DATABASE_URL,
    override_get_db_connection,
    load_test_data,
    test_db,
    load_and_rollback_test_data,
)
from ..app.main import app
from ..app.models import db

app.dependency_overrides[db.get_database_connection] = override_get_db_connection

client = TestClient(app)


###############
# /ingredients/
###############


@load_and_rollback_test_data("simple_recipes.json")
def test_get_ingredient_list(test_db):
    """GET /ingredients/"""

    response = client.get("/ingredients/")

    assert response.status_code == 200
    db_ingredients = test_db.execute(db.ingredients.select()).fetchall()
    assert len(response.json()) == len(db_ingredients)


@load_and_rollback_test_data("simple_recipes.json")
def test_post_ingredient(test_db):
    """POST /ingredients/"""
    response = client.post("/ingredients/", json={"name": "test"})

    assert response.status_code == 201
    data = response.json()
    db_ingredient = test_db.execute(
        db.ingredients.select().where(db.ingredients.c.id == data["id"])
    )
    assert db_ingredient is not None


@load_and_rollback_test_data("simple_recipes.json")
def test_post_ingredient_already_exists(test_db):

    response = client.post("/ingredients/", json={"name": "Cumin"})

    assert response.status_code == 422


#########################
# /ingredients/{id: int}/
#########################


@load_and_rollback_test_data("simple_recipes.json")
def test_get_ingredient_detail(test_db):
    """GET /ingredient/pk/
    """
    response = client.get("/ingredients/1/")
    assert response.status_code == 200
