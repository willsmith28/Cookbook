"""RecipeManager Tests
"""
# pylint: disable=import-error
from django.test import TestCase, Client
from django.urls import reverse
from model_bakery import baker, seq
from users.models import User
from . import models

TEST_USER_NAME = "testUser"
TEST_EMAIL = "test@test.net"
TEST_USER_NAME1 = "testUser1"
TEST_EMAIL1 = "test1@test.net"
TEST_PASSWORD = "abc123"


def get_token(user_name=TEST_USER_NAME, password=TEST_PASSWORD):
    """Gets user Token
    Args:
        user_name (str, optional): username to login. Defaults to TEST_USER_NAME.
        password (str, optional): password to login. Defaults to TEST_PASSWORD.

    Returns:
        str: user token
    """
    client = Client()
    response = client.post(
        "/api-token-auth/", {"username": user_name, "password": password}
    )
    response_data = response.json()
    return response_data["token"]


class IngredientTestCase(TestCase):
    """Tests for /ingredient/
    """

    def setUp(self):
        User.objects.create_user(
            TEST_USER_NAME, email=TEST_EMAIL, password=TEST_PASSWORD
        )

        self.ingredient1 = baker.make(models.Ingredient)
        self.ingredient2 = baker.make(models.Ingredient)
        self.ingredient3 = baker.make(models.Ingredient)

        self.ingredients = [self.ingredient1, self.ingredient2, self.ingredient3]

    def test_get_ingredients_list(self):
        """
        GET /ingredient/
        """
        response = self.client.get(reverse("ingredient"))
        response_data = response.json()
        self.assertEqual(len(response_data), len(self.ingredients))

    def test_post_ingredient(self):
        """
        POST /ingredient/
        """
        token = get_token()
        test_ingredient = {"name": "chicken"}
        response = self.client.post(
            reverse("ingredient"),
            test_ingredient,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {token}",
        )
        response_data = response.json()
        self.assertIn("id", response_data)
        self.assertEqual(response_data["name"], test_ingredient["name"])

    def test_post_ingredient_already_exists(self):
        """
        POST /ingredient/
        """
        token = get_token()
        test_ingredient = {"name": "chicken"}
        response_success = self.client.post(
            reverse("ingredient"),
            test_ingredient,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {token}",
        )
        self.assertEqual(response_success.status_code, 201)
        response_conflict = self.client.post(
            reverse("ingredient"),
            test_ingredient,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {token}",
        )
        self.assertEqual(response_conflict.status_code, 409)
        self.assertEqual(response_success.json()["id"], response_conflict.json()["id"])

    def test_get_ingredient_detail(self):
        """
        GET /ingredient/<int:pk>/
        """
        response = self.client.get(
            reverse("ingredient-detail", kwargs={"pk": self.ingredient1.id})
        )
        response_data = response.json()
        self.assertEqual(response_data["id"], self.ingredient1.id)


class TagTestCase(TestCase):
    """Tests for /tag/
    """

    def setUp(self):
        User.objects.create_user(
            TEST_USER_NAME, email=TEST_EMAIL, password=TEST_PASSWORD
        )

        self.tag1 = baker.make(models.Tag)
        self.tag2 = baker.make(models.Tag)
        self.tag3 = baker.make(models.Tag)

        self.tags = [self.tag1, self.tag2, self.tag3]

    def test_get_tag_list(self):
        """
        GET /tag/
        """
        response = self.client.get(reverse("tag"))
        response_data = response.json()
        self.assertEqual(len(response_data), len(self.tags))

    def test_tag_post(self):
        """
        POST /tag/
        """
        token = get_token()
        response = self.client.post(
            reverse("tag"),
            {"value": "slow cooker"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {token}",
        )
        self.assertIn("id", response.json())
        self.assertEqual(response.status_code, 201)

    def test_tag_post_already_exists(self):
        """
        Post /tag/ already exists
        """
        token = get_token()
        test_tag = {"value": "slow cooker"}
        success_response = self.client.post(
            reverse("tag"),
            test_tag,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {token}",
        )
        self.assertEqual(success_response.status_code, 201)
        conflict_response = self.client.post(
            reverse("tag"),
            test_tag,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {token}",
        )
        self.assertEqual(conflict_response.status_code, 409)
        self.assertEqual(success_response.json()["id"], conflict_response.json()["id"])

    def test_get_tag_detail(self):
        """
        GET /tag/<int:pk>/
        """
        response = self.client.get(reverse("tag-detail", kwargs={"pk": self.tag1.id}))
        response_data = response.json()
        self.assertEqual(response_data["id"], self.tag1.id)


class RecipeTestCase(TestCase):
    """Tests for /recipe/
    """

    def setUp(self):
        self.user = User.objects.create_user(
            TEST_USER_NAME, email=TEST_EMAIL, password=TEST_PASSWORD
        )
        User.objects.create_user(
            TEST_USER_NAME1, email=TEST_EMAIL1, password=TEST_PASSWORD
        )

        self.test_recipe = {
            "name": "some name",
            "description": "some description",
            "servings": 4,
            "cook_time": "1  hour",
            "ingredients": [
                {
                    "name": "chicken",
                    "amount": 4,
                    "unit": "n/a",
                    "specifier": "",
                    "recipe_id": None,
                }
            ],
            "steps": [
                {"order": 1, "instruction": "cut chicken"},
                {"order": 2, "instruction": "cook chicken"},
            ],
            "tags": [{"value": "chicken"}],
        }

        steps = [models.Step(order=i + 1, instruction="do thing") for i in range(5)]
        ingredient_set = baker.prepare(models.Ingredient, _quantity=5)
        self.recipe1 = baker.make(
            models.Recipe,
            # make_m2m=True,
            steps=steps,
            ingredients=ingredient_set,
            servings=seq(5),
            author=self.user,
        )

        self.recipes = [self.recipe1]

    def test_get_recipe_list(self):
        """
        GET /recipe/
        """
        response = self.client.get(reverse("recipe"))

        recipes = response.json()
        self.assertEqual(len(recipes), len(self.recipes))

    def test_ingredients_not_in_recipe_list(self):
        """
        GET /recipe/
        """
        response = self.client.get(reverse("recipe"))

        recipes = response.json()
        recipe = recipes[0]
        self.assertNotIn("ingredients", recipe)

    def test_post_recipe(self):
        """
        POST /recipe/
        """
        token = get_token()
        response = self.client.post(
            reverse("recipe"),
            self.test_recipe,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {token}",
        )
        response_data = response.json()
        recipe_from_db = models.Recipe.objects.get(name=self.test_recipe["name"])
        self.assertEqual(response_data["id"], recipe_from_db.id)

    def test_unauthorized_post_recipe(self):
        """
        POST /recipe/
        not logged in
        """
        response = self.client.post(
            reverse("recipe"), self.test_recipe, content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

    def test_recipe_name_integrity(self):
        """
        POST /recipe/
        already taken name
        """
        token = get_token()
        response_success = self.client.post(  # noqa: F841
            reverse("recipe"),
            self.test_recipe,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {token}",
        )
        self.assertEqual(response_success.status_code, 201)
        response_failure = self.client.post(
            reverse("recipe"),
            self.test_recipe,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {token}",
        )
        self.assertEqual(response_failure.status_code, 400)

    def test_recipe_non_sequential_steps(self):
        """
        POST /recipe/
        invalid steps
        """
        token = get_token()
        test_recipe = self.test_recipe.copy()
        test_recipe["steps"].append({"order": 10, "instruction": "eat chicken"})
        response = self.client.post(
            reverse("recipe"),
            test_recipe,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {token}",
        )
        self.assertEqual(response.status_code, 400)

    def test_get_recipe_detail(self):
        """
        GET /recipe/<int:pk>/
        """
        response = self.client.get(
            reverse("recipe-detail", kwargs={"pk": self.recipe1.id})
        )
        recipe = response.json()
        self.assertEqual(recipe["id"], self.recipe1.id)

    def test_amount_in_the_recipe_ingredient(self):
        """
        GET /recipe/<int:pk>/
        'amount' in recipe.ingredients[0]
        """
        response = self.client.get(
            reverse("recipe-detail", kwargs={"pk": self.recipe1.id})
        )
        recipe = response.json()
        self.assertIn("amount", recipe["ingredients"][0])

    def test_edit_recipe_detail(self):
        """
        PUT /recipe/<int:pk>/
        """
        token = get_token()
        updated_recipe = {
            **self.recipe1.to_json(),
            "name": "new_name",
        }
        updated_recipe.pop("created_on")
        updated_recipe.pop("last_updated_on")

        self.client.put(
            reverse("recipe-detail", kwargs={"pk": self.recipe1.id}),
            updated_recipe,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {token}",
        )

        recipe_from_db = models.Recipe.objects.get(id=self.recipe1.id)
        self.assertEqual(updated_recipe["name"], recipe_from_db.name)

    def test_edit_recipe_different_user_detail(self):
        """
        PUT /recipe/<int:pk>/
        different user
        """
        token = get_token(TEST_USER_NAME1, TEST_PASSWORD)
        updated_recipe = {
            **self.recipe1.to_json(),
            "name": "new_name",
        }
        response = self.client.put(
            reverse("recipe-detail", kwargs={"pk": self.recipe1.id}),
            updated_recipe,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {token}",
        )
        self.assertEqual(response.status_code, 403)

    def test_edit_recipe_detail_remove_step(self):
        """
        PUT /recipe/<int:pk>/
        invalid
        """
        token = get_token()
        updated_recipe = {
            **self.recipe1.to_json(),
            "steps": [step.to_json() for step in list(self.recipe1.steps.all())[:-1]],
        }
        self.client.put(
            reverse("recipe-detail", kwargs={"pk": self.recipe1.id}),
            updated_recipe,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {token}",
        )

        recipe_from_db = models.Recipe.objects.get(id=self.recipe1.id)
        self.assertEqual(len(updated_recipe["steps"]), recipe_from_db.steps.count())

    def test_recipe_ingredient_get_list(self):
        """
        GET /recipe/<int:pk>/ingredients/
        """
        response = self.client.get(
            reverse("recipe-ingredients", kwargs={"recipe_pk": self.recipe1.id})
        )
        response_data = response.json()
        self.assertEqual(len(response_data), self.recipe1.ingredients.count())

    def test_recipe_ingredient_post(self):
        """
        POST /recipe/<int:pk>/ingredients/
        """
        token = get_token()
        test_recipe_ingredient = {
            "unit": "tsp",
            "amount": 0.5,
            "name": "cumin",
            "specifier": "",
            "recipe_id": None,
        }
        response = self.client.post(
            reverse("recipe-ingredients", kwargs={"recipe_pk": self.recipe1.id}),
            test_recipe_ingredient,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {token}",
        )
        self.assertEqual(response.status_code, 201)

    def test_recipe_ingredient_different_user_post(self):
        """
        POST /recipe/<int:pk>/ingredients/
        """
        token = get_token(TEST_USER_NAME1, TEST_PASSWORD)
        test_recipe_ingredient = {
            "unit": "tsp",
            "amount": 0.5,
            "name": "cumin",
            "specifier": "",
            "recipe_id": None,
        }
        response = self.client.post(
            reverse("recipe-ingredients", kwargs={"recipe_pk": self.recipe1.id}),
            test_recipe_ingredient,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {token}",
        )
        self.assertEqual(response.status_code, 403)

    def test_recipe_ingredient_detail_get(self):
        """
        GET /recipe/<int:recipe_pk>/ingredients/<int:ingredient_pk>/
        """
        recipe_ingredient_id = self.recipe1.ingredients.first().id
        response = self.client.get(
            reverse(
                "recipe-ingredient-detail",
                kwargs={
                    "recipe_pk": self.recipe1.id,
                    "ingredient_pk": recipe_ingredient_id,
                },
            )
        )
        response_data = response.json()
        self.assertEqual(response_data["ingredient_id"], recipe_ingredient_id)

    def test_recipe_ingredient_detail_put(self):
        """
        PUT /recipe/<int:recipe_pk>/ingredients/<int:ingredient_pk>/
        """
        token = get_token()
        recipe_ingredient = models.IngredientInRecipe.objects.get(
            parent_recipe_id=self.recipe1, ingredient=self.recipe1.ingredients.first(),
        )
        test_recipe_ingredient = {
            **recipe_ingredient.to_json(),
            "amount": recipe_ingredient.amount + 1,
        }
        response = self.client.put(
            reverse(
                "recipe-ingredient-detail",
                kwargs={
                    "recipe_pk": self.recipe1.id,
                    "ingredient_pk": recipe_ingredient.id,
                },
            ),
            test_recipe_ingredient,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {token}",
        )
        response_data = response.json()
        self.assertEqual(response_data["amount"], str(recipe_ingredient.amount + 1))

    def test_recipe_ingredient_detail_put_different_user(self):
        """
        PUT /recipe/<int:recipe_pk>/ingredients/<int:ingredient_pk>/
        """
        token = get_token(TEST_USER_NAME1, TEST_PASSWORD)
        recipe_ingredient = models.IngredientInRecipe.objects.get(
            parent_recipe_id=self.recipe1, ingredient=self.recipe1.ingredients.first()
        )
        test_recipe_ingredient = {
            **recipe_ingredient.to_json(),
            "amount": recipe_ingredient.amount + 1,
        }
        response = self.client.put(
            reverse(
                "recipe-ingredient-detail",
                kwargs={
                    "recipe_pk": self.recipe1.id,
                    "ingredient_pk": recipe_ingredient.id,
                },
            ),
            test_recipe_ingredient,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {token}",
        )
        self.assertEqual(response.status_code, 403)

    def test_recipe_ingredient_detail_delete(self):
        """
        DELETE /recipe/<int:recipe_pk>/ingredients/<int:ingredient_pk>/
        """
        token = get_token()
        recipe_ingredient = models.IngredientInRecipe.objects.get(
            parent_recipe_id=self.recipe1, ingredient=self.recipe1.ingredients.first()
        )
        recipe_ingredient_count_pre_delete = self.recipe1.ingredients.count()
        response = self.client.delete(
            reverse(
                "recipe-ingredient-detail",
                kwargs={
                    "recipe_pk": self.recipe1.id,
                    "ingredient_pk": recipe_ingredient.ingredient_id,
                },
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {token}",
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(
            self.recipe1.ingredients.count(), recipe_ingredient_count_pre_delete - 1
        )
