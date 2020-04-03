"""
Views for /recipe/<recipe_pk>/ingredients/ and /recipe/<recipe_pk>/ingredients/<ingredient_pk>
"""
from django.db import IntegrityError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status
from .. import models, utils, constants


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
            response = Response(
                {"message": "Recipe was not found"}, status=status.HTTP_404_NOT_FOUND
            )

        else:
            response = Response(
                tuple(
                    ingredient.to_json()
                    for ingredient in models.IngredientInRecipe.objects.filter(
                        parent_recipe_id=recipe.id
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
        recipe_ingredient = request.data

        try:
            recipe = models.Recipe.objects.get(id=recipe_pk)
            ingredient = models.Ingredient.objects.get(
                id=recipe_ingredient["ingredient_id"]
            )
        except models.Recipe.DoesNotExist:
            return Response(
                {"message": "Recipe was not found"}, status=status.HTTP_404_NOT_FOUND
            )

        except models.Ingredient.DoesNotExist:
            return Response(
                {"message": "Invalid ingredient_id"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not utils.user_owns_item(
            recipe.author_id, request.user.id, request.user.is_superuser
        ):
            return constants.NOT_ALLOWED_RESPONSE

        if errors := utils.validate_required_fields(
            recipe_ingredient, constants.REQUIRED_INGREDIENT_IN_RECIPE_FIELDS
        ):
            return Response(
                {"message": ". ".join(errors)}, status=status.HTTP_400_BAD_REQUEST
            )

        recipe_ingredient = utils.extract_required_fields(
            recipe_ingredient, constants.REQUIRED_INGREDIENT_IN_RECIPE_FIELDS
        )

        try:
            recipe_ingredient = models.IngredientInRecipe.objects.create(
                parent_recipe_id=recipe.id, ingredient=ingredient, **recipe_ingredient,
            )

        except IntegrityError as err:
            response = Response(
                {"message": str(err.__cause__)}, status=status.HTTP_400_BAD_REQUEST
            )

        else:
            response = Response(
                recipe_ingredient.to_json(), status=status.HTTP_201_CREATED,
            )

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
            recipe_ingredient = models.IngredientInRecipe.objects.get(
                ingredient_id=ingredient_pk, parent_recipe_id=recipe_pk
            )

        except models.IngredientInRecipe.DoesNotExist:
            response = Response(
                {"message": "Ingredient on that recipe was not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        else:
            response = Response(recipe_ingredient.to_json(), status=status.HTTP_200_OK,)

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
            recipe_ingredient = models.IngredientInRecipe.objects.select_related(
                "ingredient", "parent_recipe"
            ).get(ingredient_id=ingredient_pk, parent_recipe_id=recipe_pk)

        except models.IngredientInRecipe.DoesNotExist:
            return Response(
                {"message": "Ingredient on that recipe was not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user.id != recipe_ingredient.parent_recipe.author_id:
            if not request.user.is_superuser:
                return Response(
                    {"message": "Cannot edit a recipe that is not yours"},
                    status=status.HTTP_403_FORBIDDEN,
                )

        request_recipe_ingredient = utils.extract_required_fields(
            request.data, constants.REQUIRED_INGREDIENT_IN_RECIPE_FIELDS
        )

        edited = False
        for key, value in request_recipe_ingredient.items():
            if value is not None and value != getattr(recipe_ingredient, key):
                setattr(recipe_ingredient, key, value)
                edited = True

        try:
            if edited:
                recipe_ingredient.save()

        except IntegrityError as err:
            response = Response(
                {"message": str(err.__cause__)}, status=status.HTTP_409_CONFLICT
            )
        else:
            response = Response(recipe_ingredient.to_json(), status=status.HTTP_200_OK,)

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
            models.Recipe.objects.values("id").get(id=recipe_pk)
            recipe_ingredient = models.IngredientInRecipe.objects.get(
                ingredient_id=ingredient_pk, parent_recipe_id=recipe_pk
            )
        except models.Recipe.DoesNotExist:
            response = Response(
                {"message": "Recipe with that id was not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        except models.IngredientInRecipe.DoesNotExist:
            response = Response(
                {"message": "Ingredient on that recipe was not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        else:
            recipe_ingredient.delete()
            response = Response(status=status.HTTP_204_NO_CONTENT)

        return response
