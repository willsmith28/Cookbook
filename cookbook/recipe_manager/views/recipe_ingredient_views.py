"""
Views for /recipe/<recipe_pk>/ingredients/ and /recipe/<recipe_pk>/ingredients/<ingredient_pk>
"""
from django.db import IntegrityError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status
from ..serializers import IngredientInRecipeSerializer
from .. import models, utils


class RecipeIngredient(APIView):
    """
    [GET, POST] /recipe/<int:recipe_pk>/ingredients/
    {
        amount: decimal,
        unit: str,
        specifier: str,
        ingredient_id: (int, str)
    }
    """

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, recipe_pk):
        """Get a list of ingredients in a recipe

        Args:
            request (HttpRequest): Django HttpRequest
            recipe_pk (int): Recipe primary key

        Returns:
            Response: DRF Response
        """
        try:
            recipe = models.Recipe.objects.get(id=recipe_pk)

        except models.Recipe.DoesNotExist:
            response = Response(status=status.HTTP_404_NOT_FOUND)

        else:
            response = Response(
                tuple(
                    IngredientInRecipeSerializer(ingredient).data
                    for ingredient in models.IngredientInRecipe.objects.filter(
                        recipe_id=recipe.id
                    )
                ),
                status=status.HTTP_200_OK,
            )

        return response

    def post(self, request, recipe_pk):
        """Add ingredient to recipe

        Args:
            request (HttpRequest): Django HttpRequest
            recipe_pk (int): Recipe primary key

        Returns:
            Response: DRF Response
        """

        try:
            recipe = models.Recipe.objects.get(id=recipe_pk)

        except models.Recipe.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND,)

        if not utils.user_owns_item(
            recipe.author_id, request.user.id, request.user.is_superuser
        ):
            return Response(
                {
                    "errors": {
                        "non_field_errors": (
                            "You cannot add ingredients to a recipe that is not yours",
                        )
                    }
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        data = {**request.data, "recipe_id": recipe.id}
        serializer = IngredientInRecipeSerializer(data=data)

        if not serializer.is_valid():
            return Response(
                {"errors": utils.serialize_errors(serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            serializer.save()

        except IntegrityError as err:
            response = Response(
                {"errors": {"non_field_errors": [str(err.__cause__)]}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        else:
            response = Response(serializer.data, status=status.HTTP_201_CREATED,)

        return response


class RecipeIngredientDetail(APIView):
    """
    [GET, PUT, DELETE]
    /recipe/<int:recipe_pk>/ingredients/<int:ingredient_pk>/
    {
        amount: decimal, str,
        unit: str,
        specifier: str,
        ingredient_id: int
        GET only
        name: str
        recipe_id: int
    }
    """

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, recipe_pk, ingredient_pk):
        """
        Get Ingredient in recipe detail

        Args:
            request (HttpRequest): Django HttpRequest
            recipe_pk (int): Recipe primary key
            ingredient_pk (int): Ingredient primary key

        Returns:
            Response: DRF Response
        """
        try:
            ingredient_in_recipe = models.IngredientInRecipe.objects.get(
                ingredient_id=ingredient_pk, recipe_id=recipe_pk
            )

        except models.IngredientInRecipe.DoesNotExist:
            response = Response(status=status.HTTP_404_NOT_FOUND,)
        else:
            response = Response(
                IngredientInRecipeSerializer(ingredient_in_recipe).data,
                status=status.HTTP_200_OK,
            )

        return response

    def put(self, request, recipe_pk, ingredient_pk):
        """
        Edit Ingredient in recipe

        Args:
            request (HttpRequest): Django HttpRequest
            recipe_pk (int): Recipe primary key
            ingredient_pk (int): Ingredient primary key

        Returns:
            Response: DRF Response
        """
        try:
            ingredient_in_recipe = models.IngredientInRecipe.objects.select_related(
                "ingredient", "recipe"
            ).get(ingredient_id=ingredient_pk, recipe_id=recipe_pk)

        except models.IngredientInRecipe.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND,)

        if not utils.user_owns_item(
            ingredient_in_recipe.recipe.author_id,
            request.user.id,
            request.user.is_superuser,
        ):
            return Response(
                {
                    "errors": {
                        "non_field_errors": (
                            "You cannot edit ingredients in a recipe that is not yours",
                        )
                    }
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        data = {**request.data, "recipe_id": recipe_pk, "ingredient_id": ingredient_pk}

        serializer = IngredientInRecipeSerializer(ingredient_in_recipe, data=data)

        if not serializer.is_valid():
            return Response(
                {"errors": utils.serialize_errors(serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            serializer.save()

        except IntegrityError as err:
            response = Response(
                {"errors": {"non_field_errors": (str(err.__cause__),)}},
                status=status.HTTP_409_CONFLICT,
            )
        else:
            response = Response(serializer.data, status=status.HTTP_200_OK,)

        return response

    def delete(self, request, recipe_pk, ingredient_pk):
        """
        Remove Ingredient from recipe

        Args:
            request (HttpRequest): Django HttpRequest
            recipe_pk (int): Recipe primary key
            ingredient_pk (int): Ingredient primary key

        Returns:
            Response: DRF Response
        """
        try:
            recipe_ingredient = models.IngredientInRecipe.objects.get(
                ingredient_id=ingredient_pk, recipe_id=recipe_pk
            )

        except models.IngredientInRecipe.DoesNotExist:
            response = Response(status=status.HTTP_404_NOT_FOUND,)

        else:
            recipe_ingredient.delete()
            response = Response(status=status.HTTP_204_NO_CONTENT)

        return response
