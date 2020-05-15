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

        def add_errors_to_dict(errors, key, serializers):
            for index, serializer in serializers:
                errors[key][index] = {
                    key: tuple(str(error) for error in errors)
                    for key, errors in serializer.errors.items()
                }

        user = request.user
        data = {**request.data, "author_id": user.id}
        errors = {}

        try:
            ingredient_in_recipe_serializers = tuple(
                IngredientInRecipeSerializer(data=ingredient)
                for ingredient in data.pop("ingredients", ())
            )
            step_serializers = tuple(
                StepSerializer(data=step) for step in data.pop("steps", ())
            )
            tag_ids = tuple(tag_id for tag_id in data.pop("tags", ()))
        except TypeError:
            return Response(
                {
                    "errors": {
                        "message": '"ingredients", "steps", and "tags" must all be Arrays'
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        recipe_serializer = RecipeSerializer(data=data)

        if not recipe_serializer.is_valid():
            errors["recipe"] = {
                key: tuple(str(error) for error in errors)
                for key, errors in recipe_serializer.errors.items()
            }

        if invalid_serializers := tuple(
            (str(index), serializer)
            for index, serializer in enumerate(ingredient_in_recipe_serializers)
            if not serializer.is_valid()
        ):
            errors["ingredients"] = {}
            add_errors_to_dict(errors, "ingredients", invalid_serializers)

        if invalid_serializers := tuple(
            (str(index), serializer)
            for index, serializer in enumerate(step_serializers)
            if not serializer.is_valid()
        ):
            errors["steps"] = {}
            add_errors_to_dict(errors, "steps", invalid_serializers)

        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                recipe_instance = recipe_serializer.save()
                for serializer in ingredient_in_recipe_serializers:
                    ingredient = serializer.data
                    recipe_instance.ingredients.add(
                        models.Ingredient.objects.get(
                            id=ingredient.pop("ingredient_id")
                        ),
                        through_defaults=ingredient,
                    )

                for index, serializer in enumerate(step_serializers, 1):
                    step = serializer.data
                    recipe_instance.steps.create(
                        instruction=step["instruction"], order=index
                    )

                for tag_id in tag_ids:
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

        request_recipe = utils.extract_required_fields(
            request.data, constants.REQUIRED_RECIPE_FIELDS
        )
        edit = False

        for field, value in request_recipe.items():
            if value is not None and value != getattr(recipe, field):
                setattr(recipe, field, value)
                edit = True

        try:
            if edit:
                recipe.save()

        except IntegrityError as err:
            response = Response(
                {"message": str(err.__cause__)}, status=status.HTTP_400_BAD_REQUEST
            )

        else:
            response = Response(
                recipe.to_json(
                    with_ingredient_ids=True, with_step_ids=True, with_tag_ids=True
                ),
                status=status.HTTP_200_OK,
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
