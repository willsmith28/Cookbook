"""
Views for /recipe/ and /recipe/<pk>/
"""
from django.db import transaction, IntegrityError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status
from ..serializers import (
    RecipeSerializer,
    IngredientInRecipeSerializer,
    StepSerializer,
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
        steps: [
            {
                'order': int,
                'instruction': str,
                'recipe_id': int # does not need to be provided
            }
        ],
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

        def serialize_recipes_with_fk_ids(recipes):
            for recipe in recipes:
                yield _serialize_recipe_with_fk_ids(recipe)

        recipes = models.Recipe.objects.prefetch_related(
            "ingredients", "steps", "tags"
        ).all()

        return Response(
            tuple(serialize_recipes_with_fk_ids(recipes)), status=status.HTTP_200_OK,
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
                recipe_instance = serializers["recipe"].save()
                for serializer in serializers["ingredients"]:
                    ingredient = serializer.data
                    recipe_instance.ingredients.add(
                        models.Ingredient.objects.get(
                            id=ingredient.pop("ingredient_id")
                        ),
                        through_defaults=ingredient,
                    )

                for serializer in serializers["steps"]:
                    step = serializer.data
                    recipe_instance.steps.create(**step)

                for tag_id in serializers["tag_ids"]:
                    try:
                        recipe_instance.tags.add(models.Tag.objects.get(id=tag_id))

                    except models.Tag.DoesNotExist:
                        pass

        except models.Ingredient.DoesNotExist:
            response = Response(
                {"message": "A provided ingredient ID does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except IntegrityError as err:
            response = Response(
                {"message": str(err.__cause__)}, status=status.HTTP_400_BAD_REQUEST
            )

        else:
            response = Response(
                _serialize_recipe_with_fk_ids(recipe_instance),
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
        ingredients: [int,],
        steps: [int,],
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
            recipe = models.Recipe.objects.prefetch_related(
                "tags", "steps", "ingredients"
            ).get(id=pk)

        except models.Recipe.DoesNotExist:
            response = Response(
                {"message": "No Recipe was found with that ID"},
                status=status.HTTP_404_NOT_FOUND,
            )

        else:
            response = Response(
                _serialize_recipe_with_fk_ids(recipe), status=status.HTTP_200_OK,
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
            recipe = models.Recipe.objects.prefetch_related(
                "tags", "steps", "ingredients"
            ).get(id=pk)

        except models.Recipe.DoesNotExist:
            return Response(
                {"message": "No Recipe was found with that ID"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not utils.user_owns_item(
            recipe.author_id, request.user.id, request.user.is_superuser
        ):
            return constants.NOT_ALLOWED_RESPONSE

        recipe_serializer = RecipeSerializer(
            recipe, data={**request.data, "author_id": request.user.id}
        )

        if recipe_serializer.is_valid():
            try:
                recipe = recipe_serializer.save()

            except IntegrityError as err:
                return Response(
                    {"message": str(err.__cause__)}, status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            _serialize_recipe_with_fk_ids(recipe), status=status.HTTP_200_OK
        )


def _serialize_recipe_with_fk_ids(recipe: models.Recipe) -> dict:
    serialized_recipe = RecipeSerializer(recipe).data
    serialized_recipe["tags"] = tuple(
        int(tag_id) for tag_id in recipe.tags.values_list("id", flat=True).all()
    )
    serialized_recipe["ingredients"] = tuple(
        int(ingredient_id)
        for ingredient_id in recipe.ingredients.values_list("id", flat=True).all()
    )
    serialized_recipe["steps"] = tuple(
        int(step_id) for step_id in recipe.steps.values_list("id", flat=True).all()
    )
    return serialized_recipe
