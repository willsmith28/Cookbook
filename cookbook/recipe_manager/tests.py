"""RecipeManager Tests
"""
# pylint: disable=import-error,too-many-public-methods
from django.test import TestCase, Client
from django.urls import reverse
from model_bakery import baker, seq
from users.models import User
from . import models, constants, serializers

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
        reverse("token_obtain_pair"),
        {"username": user_name, "password": password},
        content_type="application/json",
    )
    response_data = response.json()
    return f'Bearer {response_data["access"]}'


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

    def test_get_ingredients_list(self):
        """
        GET /ingredient/
        """
        response = self.client.get(reverse("ingredient"))
        response_data = response.json()
        self.assertEqual(len(response_data), models.Ingredient.objects.count())

    def test_post_ingredient(self):
        """
        POST /ingredient/
        """
        token = get_token()
        test_ingredient = {"name": "chicken", "recipe_id": None}
        response = self.client.post(
            reverse("ingredient"),
            test_ingredient,
            content_type="application/json",
            HTTP_AUTHORIZATION=token,
        )
        response_data = response.json()
        self.assertIn("id", response_data)
        self.assertEqual(response_data["name"], test_ingredient["name"])

    def test_post_ingredient_already_exists(self):
        """
        POST /ingredient/ unique conflict
        """
        token = get_token()
        test_ingredient = {"name": "chicken", "recipe_id": None}
        response_success = self.client.post(
            reverse("ingredient"),
            test_ingredient,
            content_type="application/json",
            HTTP_AUTHORIZATION=token,
        )
        self.assertEqual(response_success.status_code, 201)
        response_conflict = self.client.post(
            reverse("ingredient"),
            test_ingredient,
            content_type="application/json",
            HTTP_AUTHORIZATION=token,
        )
        self.assertEqual(response_conflict.status_code, 400)

    def test_get_ingredient_detail(self):
        """
        GET /ingredient/<int:pk>/
        """
        response = self.client.get(
            reverse("ingredient-detail", kwargs={"pk": self.ingredient1.id})
        )
        response_data = response.json()
        self.assertEqual(response_data["id"], self.ingredient1.id)
        self.assertIn("name", response.json())


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

    def test_get_tag_list(self):
        """
        GET /tag/
        """
        response = self.client.get(reverse("tag"))
        response_data = response.json()
        self.assertEqual(len(response_data), models.Tag.objects.count())

    def test_tag_post(self):
        """
        POST /tag/
        """
        token = get_token()
        response = self.client.post(
            reverse("tag"),
            {"value": "slow cooker", "kind": "Prep Method"},
            content_type="application/json",
            HTTP_AUTHORIZATION=token,
        )
        self.assertIn("id", response.json())
        self.assertEqual(response.status_code, 201)

    def test_tag_post_already_exists(self):
        """
        Post /tag/ already exists
        """
        token = get_token()
        test_tag = {"value": "slow cooker", "kind": "Prep Method"}
        success_response = self.client.post(
            reverse("tag"),
            test_tag,
            content_type="application/json",
            HTTP_AUTHORIZATION=token,
        )
        self.assertEqual(success_response.status_code, 201)
        conflict_response = self.client.post(
            reverse("tag"),
            test_tag,
            content_type="application/json",
            HTTP_AUTHORIZATION=token,
        )
        self.assertEqual(conflict_response.status_code, 409)

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

        steps = [models.Step(order=i + 1, instruction="do thing") for i in range(5)]
        ingredient_set = baker.prepare(models.Ingredient, _quantity=5)
        tag_set = baker.prepare(models.Tag, _quantity=5)
        self.recipe1 = baker.make(
            models.Recipe,
            # make_m2m=True,
            steps=steps,
            ingredients=ingredient_set,
            servings=seq(5),
            author=self.user,
            tags=tag_set,
        )

        self.ingredient1 = baker.make(models.Ingredient, recipe_id=None)

        self.test_valid_recipe = {
            "name": "some name",
            "description": "some description",
            "servings": 4,
            "cook_time": "1  hour",
            "tags": [int(tag.id) for tag in tag_set],
        }
        self.test_invalid_recipe = {
            "name": "",
            "description": {},
            "servings": "3",
            "cook_time": 6,
        }

    def test_get_recipe_list(self):
        """
        GET /recipe/
        """
        response = self.client.get(reverse("recipe"))

        recipes = response.json()
        self.assertEqual(len(recipes), models.Recipe.objects.count())

    def test_post_valid_recipe(self):
        """
        POST /recipe/ valid data
        """
        token = get_token()
        response = self.client.post(
            reverse("recipe"),
            self.test_valid_recipe,
            content_type="application/json",
            HTTP_AUTHORIZATION=token,
        )
        response_data = response.json()
        recipe_from_db = models.Recipe.objects.get(name=self.test_valid_recipe["name"])
        self.assertEqual(response_data["id"], recipe_from_db.id)

    def test_post_invalid_recipe(self):
        """
        POST /recipe/ invalid data
        """
        token = get_token()
        response = self.client.post(
            reverse("recipe"),
            self.test_invalid_recipe,
            content_type="application/json",
            HTTP_AUTHORIZATION=token,
        )
        self.assertEqual(response.status_code, 400)

    def test_post_valid_recipe_invalid_tags(self):
        """
        POST /recipe/ invalid data
        """
        token = get_token()
        response = self.client.post(
            reverse("recipe"),
            {**self.test_valid_recipe, "tags": 3},
            content_type="application/json",
            HTTP_AUTHORIZATION=token,
        )
        self.assertEqual(response.status_code, 400)

    def test_unauthorized_post_recipe(self):
        """
        POST /recipe/
        not logged in
        """
        response = self.client.post(
            reverse("recipe"), self.test_valid_recipe, content_type="application/json",
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
            self.test_valid_recipe,
            content_type="application/json",
            HTTP_AUTHORIZATION=token,
        )
        self.assertEqual(response_success.status_code, 201)
        response_failure = self.client.post(
            reverse("recipe"),
            self.test_valid_recipe,
            content_type="application/json",
            HTTP_AUTHORIZATION=token,
        )
        self.assertEqual(response_failure.status_code, 400)

    def test_get_recipe_detail(self):
        """
        GET /recipe/<int:pk>/
        """
        response = self.client.get(
            reverse("recipe-detail", kwargs={"pk": self.recipe1.id})
        )
        recipe = response.json()
        self.assertEqual(recipe["id"], self.recipe1.id)

    def test_edit_recipe_detail(self):
        """
        PUT /recipe/<int:pk>/
        """
        token = get_token()
        updated_recipe = {
            **serializers.RecipeSerializer(self.recipe1).data,
            "name": "new_name",
        }

        updated_recipe.pop("created_on")
        updated_recipe.pop("last_updated_on")

        self.client.put(
            reverse("recipe-detail", kwargs={"pk": self.recipe1.id}),
            updated_recipe,
            content_type="application/json",
            HTTP_AUTHORIZATION=token,
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
            **serializers.RecipeSerializer(self.recipe1).data,
            "name": "new_name",
        }
        response = self.client.put(
            reverse("recipe-detail", kwargs={"pk": self.recipe1.id}),
            updated_recipe,
            content_type="application/json",
            HTTP_AUTHORIZATION=token,
        )
        self.assertEqual(response.status_code, 403)


class RecipeIngredientCase(TestCase):
    """Tests for /recipe/<recipe_pk>/ingredients/
    """

    def setUp(self):
        self.user = User.objects.create_user(
            TEST_USER_NAME, email=TEST_EMAIL, password=TEST_PASSWORD
        )
        User.objects.create_user(
            TEST_USER_NAME1, email=TEST_EMAIL1, password=TEST_PASSWORD
        )

        ingredient_set = baker.prepare(models.Ingredient, _quantity=5)
        self.recipe1 = baker.make(
            models.Recipe,
            # make_m2m=True,
            ingredients=ingredient_set,
            servings=seq(5),
            author=self.user,
        )

        self.ingredient1 = baker.make(models.Ingredient, recipe_id=None)

        self.test_recipe_ingredient = {
            "unit": "tsp",
            "amount": 0.5,
            "specifier": "",
            "ingredient_id": int(self.ingredient1.id),
        }

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
        response = self.client.post(
            reverse("recipe-ingredients", kwargs={"recipe_pk": self.recipe1.id}),
            self.test_recipe_ingredient,
            content_type="application/json",
            HTTP_AUTHORIZATION=token,
        )

        self.assertEqual(response.status_code, 201)

    def test_add_recipe_ingredient_post_invalid_id(self):
        """
        POST /recipe/<int:pk>/ingredients/
        """
        token = get_token()
        response = self.client.post(
            reverse("recipe-ingredients", kwargs={"recipe_pk": self.recipe1.id}),
            {**self.test_recipe_ingredient, "ingredient_id": 999999},
            content_type="application/json",
            HTTP_AUTHORIZATION=token,
        )

        self.assertEqual(response.status_code, 400)

    def test_add_recipe_ingredient_post_invalid_data(self):
        """
        POST /recipe/<int:pk>/ingredients/
        """
        token = get_token()
        response = self.client.post(
            reverse("recipe-ingredients", kwargs={"recipe_pk": self.recipe1.id}),
            {**self.test_recipe_ingredient, "unit": None},
            content_type="application/json",
            HTTP_AUTHORIZATION=token,
        )

        self.assertEqual(response.status_code, 400)

    def test_recipe_ingredient_different_user_post(self):
        """
        POST /recipe/<int:pk>/ingredients/
        """
        token = get_token(TEST_USER_NAME1, TEST_PASSWORD)
        response = self.client.post(
            reverse("recipe-ingredients", kwargs={"recipe_pk": self.recipe1.id}),
            self.test_recipe_ingredient,
            content_type="application/json",
            HTTP_AUTHORIZATION=token,
        )
        self.assertEqual(response.status_code, 403)

    def test_recipe_ingredient_detail_get(self):
        """
        GET /recipe/<int:recipe_pk>/ingredients/<int:ingredient_pk>/
        """
        ingredient_in_recipe = self.recipe1.ingredients.first()
        response = self.client.get(
            reverse(
                "recipe-ingredient-detail",
                kwargs={
                    "recipe_pk": self.recipe1.id,
                    "ingredient_pk": ingredient_in_recipe.id,
                },
            )
        )
        response_data = response.json()
        self.assertEqual(response_data["ingredient_id"], ingredient_in_recipe.id)
        for field in constants.REQUIRED_INGREDIENT_IN_RECIPE_FIELDS:
            self.assertIn(field, response_data)

    def test_recipe_ingredient_detail_put(self):
        """
        PUT /recipe/<int:recipe_pk>/ingredients/<int:ingredient_pk>/
        """
        token = get_token()
        recipe_ingredient = models.IngredientInRecipe.objects.get(
            recipe=self.recipe1, ingredient=self.recipe1.ingredients.first(),
        )
        test_recipe_ingredient = {
            **serializers.IngredientInRecipeSerializer(recipe_ingredient).data,
            "amount": str(recipe_ingredient.amount + 1),
            "specifier": "something new",
        }
        response = self.client.put(
            reverse(
                "recipe-ingredient-detail",
                kwargs={
                    "recipe_pk": recipe_ingredient.recipe_id,
                    "ingredient_pk": recipe_ingredient.ingredient_id,
                },
            ),
            test_recipe_ingredient,
            content_type="application/json",
            HTTP_AUTHORIZATION=token,
        )
        response_data = response.json()

        self.assertEqual(response_data["amount"], str(test_recipe_ingredient["amount"]))

    def test_recipe_ingredient_detail_put_different_user(self):
        """
        PUT /recipe/<int:recipe_pk>/ingredients/<int:ingredient_pk>/
        """
        token = get_token(TEST_USER_NAME1, TEST_PASSWORD)
        recipe_ingredient = models.IngredientInRecipe.objects.get(
            recipe=self.recipe1, ingredient=self.recipe1.ingredients.first()
        )
        test_recipe_ingredient = {
            **serializers.IngredientInRecipeSerializer(recipe_ingredient).data,
            "amount": recipe_ingredient.amount + 1,
        }
        response = self.client.put(
            reverse(
                "recipe-ingredient-detail",
                kwargs={
                    "recipe_pk": recipe_ingredient.recipe_id,
                    "ingredient_pk": recipe_ingredient.ingredient_id,
                },
            ),
            test_recipe_ingredient,
            content_type="application/json",
            HTTP_AUTHORIZATION=token,
        )
        self.assertEqual(response.status_code, 403)

    def test_recipe_ingredient_detail_delete(self):
        """
        DELETE /recipe/<int:recipe_pk>/ingredients/<int:ingredient_pk>/
        """
        token = get_token()
        recipe_ingredient = models.IngredientInRecipe.objects.get(
            recipe=self.recipe1, ingredient=self.recipe1.ingredients.first()
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
            HTTP_AUTHORIZATION=token,
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(
            self.recipe1.ingredients.count(), recipe_ingredient_count_pre_delete - 1
        )


class RecipeStepsCase(TestCase):
    """Tests for /recipe/<recipe_pk>/steps/
    """

    def setUp(self):
        self.user = User.objects.create_user(
            TEST_USER_NAME, email=TEST_EMAIL, password=TEST_PASSWORD
        )
        User.objects.create_user(
            TEST_USER_NAME1, email=TEST_EMAIL1, password=TEST_PASSWORD
        )

        steps = [models.Step(order=i + 1, instruction="do thing") for i in range(5)]
        self.recipe1 = baker.make(
            models.Recipe,
            # make_m2m=True,
            steps=steps,
            servings=seq(5),
            author=self.user,
        )

    def test_get_recipe_steps(self):
        """
        GET /recipe/<int:recipe_pk>/steps/
        """
        token = get_token()
        response = self.client.get(
            reverse("recipe-steps", kwargs={"recipe_pk": self.recipe1.id},),
            content_type="application/json",
            HTTP_AUTHORIZATION=token,
        )
        response_data = response.json()
        self.assertEqual(len(response_data), self.recipe1.steps.count())

    def test_steps_are_in_order(self):
        """
        GET /recipe/<int:recipe_pk>/steps/ Correct order
        """
        token = get_token()
        response = self.client.get(
            reverse("recipe-steps", kwargs={"recipe_pk": self.recipe1.id},),
            content_type="application/json",
            HTTP_AUTHORIZATION=token,
        )
        response_data = response.json()
        for response_instruction, db_step in zip(
            response_data, self.recipe1.steps.all()
        ):
            self.assertEqual(response_instruction, db_step.instruction)

    def test_add_step_to_recipe(self):
        """
        POST /recipe/<int:recipe_pk>/steps/
        """
        token = get_token()
        response = self.client.post(
            reverse("recipe-steps", kwargs={"recipe_pk": self.recipe1.id},),
            {"instruction": "enjoy"},
            content_type="application/json",
            HTTP_AUTHORIZATION=token,
        )
        response_data = response.json()
        step = self.recipe1.steps.all().last()
        self.assertEqual(response_data["instruction"], step.instruction)

    def test_different_user_add_step_to_recipe(self):
        """
        POST /recipe/<int:recipe_pk>/steps/
        """
        token = get_token(TEST_USER_NAME1, TEST_PASSWORD)
        response = self.client.post(
            reverse("recipe-steps", kwargs={"recipe_pk": self.recipe1.id},),
            {"instruction": "enjoy"},
            content_type="application/json",
            HTTP_AUTHORIZATION=token,
        )
        self.assertEqual(response.status_code, 403)

    def test_edit_step(self):
        """
        PUT /recipe/<int:recipe_pk>/steps/<int:order>/
        """
        token = get_token()
        test_step = {"instruction": "new"}
        db_step = self.recipe1.steps.all().first()
        response = self.client.put(
            reverse(
                "recipe-step-detail",
                kwargs={"recipe_pk": self.recipe1.id, "order": db_step.order},
            ),
            test_step,
            content_type="application/json",
            HTTP_AUTHORIZATION=token,
        )

        self.assertEqual(response.json()["instruction"], test_step["instruction"])

    def test_delete_step_isnt_last(self):
        """
        DELETE /recipe/<int:recipe_pk>/steps/<int:order>/
        """
        token = get_token()
        db_step = self.recipe1.steps.all().first()
        response = self.client.delete(
            reverse(
                "recipe-step-detail",
                kwargs={"recipe_pk": self.recipe1.id, "order": db_step.order},
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=token,
        )
        self.assertEqual(response.status_code, 409)

    def test_delete_last_step(self):
        """
        DELETE /recipe/<int:recipe_pk>/steps/<int:order>/
        """
        token = get_token()
        db_step = self.recipe1.steps.all().last()
        response = self.client.delete(
            reverse(
                "recipe-step-detail",
                kwargs={"recipe_pk": self.recipe1.id, "order": db_step.order},
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=token,
        )
        self.assertEqual(response.status_code, 204)


class RecipeTagTest(TestCase):
    """Test for Tags in Recipes
    """

    def setUp(self):
        self.user = User.objects.create_user(
            TEST_USER_NAME, email=TEST_EMAIL, password=TEST_PASSWORD
        )
        User.objects.create_user(
            TEST_USER_NAME1, email=TEST_EMAIL1, password=TEST_PASSWORD
        )

        tag_set = baker.prepare(models.Tag, _quantity=5)
        self.recipe1 = baker.make(
            models.Recipe,
            # make_m2m=True,
            servings=seq(5),
            author=self.user,
            tags=tag_set,
        )

        self.tag1 = baker.make(models.Tag)

    def test_get_recipe_tags(self):
        """
        GET /recipe/<recipe_pk>/tags/
        """
        token = get_token()
        response = self.client.get(
            reverse("recipe-tags", kwargs={"recipe_pk": self.recipe1.id},),
            content_type="application/json",
            HTTP_AUTHORIZATION=token,
        )
        self.assertEqual(len(response.json()), self.recipe1.tags.count())

    def test_add_tag_to_recipe(self):
        """
        POST /recipe/<recipe_pk>/tags/
        """
        token = get_token()
        response = self.client.post(
            reverse("recipe-tags", kwargs={"recipe_pk": self.recipe1.id},),
            {"id": self.tag1.id},
            content_type="application/json",
            HTTP_AUTHORIZATION=token,
        )
        self.assertEqual(response.status_code, 201)

    def test_add_new_tag_to_recipe(self):
        """
        POST /recipe/<recipe_pk>/tags/
        """
        token = get_token()
        response = self.client.post(
            reverse("recipe-tags", kwargs={"recipe_pk": self.recipe1.id},),
            {"value": "new tag"},
            content_type="application/json",
            HTTP_AUTHORIZATION=token,
        )
        self.assertEqual(response.status_code, 400)

    def test_add_tag_doesnt_exit_to_recipe(self):
        """
        POST /recipe/<recipe_pk>/tags/
        """
        token = get_token()
        response = self.client.post(
            reverse("recipe-tags", kwargs={"recipe_pk": self.recipe1.id},),
            {"id": 38},
            content_type="application/json",
            HTTP_AUTHORIZATION=token,
        )
        self.assertEqual(response.status_code, 400)

    def test_delete_tag_from_recipe(self):
        """
        DELETE /recipe/<recipe_pk>/tags/
        """
        token = get_token()
        tag_count_before_delete = self.recipe1.tags.all().count()
        response = self.client.delete(
            reverse(
                "recipe-tags-delete",
                kwargs={
                    "recipe_pk": self.recipe1.id,
                    "tag_pk": self.recipe1.tags.all().first().id,
                },
            ),
            {"id": 38},
            content_type="application/json",
            HTTP_AUTHORIZATION=token,
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.recipe1.tags.all().count(), tag_count_before_delete - 1)
