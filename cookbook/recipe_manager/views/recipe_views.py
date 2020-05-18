"""
Views for /recipe/ and /recipe/<pk>/
"""
from django.db import transaction, IntegrityError
from django.db.models import Prefetch
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status
from ..serializers import (
    RecipeSerializer,
    IngredientInRecipeSerializer,
)
from .. import models, utils, constants


class RecipeView(APIView):
    """
    [GET, POST]: /recipe/
    {
        name: str,
        description: str,
        servings: int,
        cook_time: str,
        tags: [int,],
        # GET
        steps: [int,],
        ingredients: [int,]
        # POST only
        steps: [str,],
        ingredients: [
            {
                amount: decimal,
                unit: str,
                specifier: str,
                recipe_id: int # does not need to be provided
                ingredient_id: int
            }
        ],
    }
    """

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request):
        """Returns a list of all Recipes

        Args:
            request (HttpRequest): Django HttpRequest

        Returns:
            Response: DRF Response
        """

        def serialize_recipes_with_relations(recipes):
            for recipe in recipes:
                yield _serialize_recipe_with_relations(recipe)

        recipes = _query_recipe_with_relations().all()

        return Response(
            tuple(serialize_recipes_with_relations(recipes)), status=status.HTTP_200_OK,
        )

    def post(self, request):
        """Create a new Recipe

        Args:
            request (HttpRequest): Django HttpRequest

        Returns:
            Response: DRF Response
        """

        user = request.user
        errors, serializers = utils.validate_recipe(
            {**request.data, "author_id": user.id}
        )

        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                recipe = serializers["recipe"].save()

                for serializer in serializers["ingredients"]:
                    ingredient = serializer.data
                    recipe.ingredients.add(
                        models.Ingredient.objects.get(
                            id=ingredient.pop("ingredient_id")
                        ),
                        through_defaults=ingredient,
                    )

                for serializer in serializers["steps"]:
                    step = serializer.data
                    recipe.steps.create(**step)

                for tag_id in serializers["tag_ids"]:
                    try:
                        recipe.tags.add(models.Tag.objects.get(id=tag_id))

                    except models.Tag.DoesNotExist:
                        pass

        except IntegrityError as err:
            response = Response(
                {"errors": {"non_field_errors": (str(err.__cause__),)}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        else:
            response = Response(
                _serialize_recipe_with_relations(recipe),
                status=status.HTTP_201_CREATED,
            )

        return response


class RecipeDetailView(APIView):
    """
    [GET, PUT]: /recipe/<int:pk>/
    {
        name: str,
        description: str,
        servings: int,
        cook_time: str,
        # GET ONLY
        ingredients: [
             {
                amount: decimal,
                unit: str,
                specifier: str,
                recipe_id: int # does not need to be provided
                ingredient_id: int
            }
        ],
        steps: [str,],
        tags: [int,]
    }
    """

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, pk):
        """Get Recipe detail

        Args:
            request (HttpRequest): Django HttpRequest
            pk (int): Recipe primary key

        Returns:
            Response: DRF Response
        """
        try:
            recipe = _query_recipe_with_relations().get(id=pk)

        except models.Recipe.DoesNotExist:
            response = Response(status=status.HTTP_404_NOT_FOUND,)

        else:
            response = Response(
                _serialize_recipe_with_relations(recipe), status=status.HTTP_200_OK,
            )

        return response

    def put(self, request, pk):
        """Edit an existing recipe

        Args:
            request (HttpRequest): Django HttpRequest
            pk (int): Recipe primary key

        Returns:
            Response: DRF Response
        """
        try:
            recipe = models.Recipe.objects.get(id=pk)

        except models.Recipe.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND,)

        if not utils.user_owns_item(
            recipe.author_id, request.user.id, request.user.is_superuser
        ):
            return constants.NOT_ALLOWED_RESPONSE

        data = {**request.data}
        data.pop("author_id", None)

        serializer = RecipeSerializer(recipe, data=data)

        if serializer.is_valid():
            try:
                serializer.save()

            except IntegrityError as err:
                return Response(
                    {"errors": {"non_field_errors": (str(err.__cause__),)}},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.data, status=status.HTTP_200_OK)


def _query_recipe_with_relations():
    return models.Recipe.objects.prefetch_related(
        "ingredients_in_recipe",
        Prefetch("steps", queryset=models.Step.objects.only("instruction")),
        Prefetch("tags", queryset=models.Tag.objects.only("id")),
    )


def _serialize_recipe_with_relations(recipe: models.Recipe) -> dict:
    serialized_recipe = RecipeSerializer(recipe).data
    serialized_recipe["ingredients"] = tuple(
        IngredientInRecipeSerializer(ingredient).data
        for ingredient in recipe.ingredients_in_recipe.all()
    )
    serialized_recipe["steps"] = tuple(
        instruction
        for instruction in recipe.steps.values_list("instruction", flat=True).all()
    )
    serialized_recipe["tags"] = tuple(
        int(tag_id) for tag_id in recipe.tags.values_list("id", flat=True).all()
    )

    return serialized_recipe
