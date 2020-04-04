"""
Views for /recipe/ and /recipe/<pk>/
"""
from django.db import transaction, IntegrityError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status
from .. import models, utils, constants


class RecipeView(APIView):
    """
    [GET, POST]: /recipe/
    {
        name: str,
        description: str,
        servings: int,
        cook_time: str,
        tags: [int,]
        # POST only
        steps: [
            {
                'order': int,
                'instruction': str,
                'recipe_id': (int, str)
            }
        ],
        ingredients: [
            {
                amount: decimal,
                unit: str,
                specifier: str,
                parent_recipe_id: int
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
        return Response(
            tuple(
                recipe.to_json(with_tag_ids=True)
                for recipe in models.Recipe.objects.prefetch_related("tags").all()
            ),
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        """Create a new Recipe

        Args:
            request (HttpRequest): Django HttpRequest

        Returns:
            Response: DRF Response
        """
        recipe = request.data
        user = request.user

        if errors := utils.validate_recipe(recipe):
            return Response(
                {"message": ". ".join(errors)}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                recipe = utils.create_recipe(recipe, user.id)

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
                recipe.to_json(
                    with_tag_ids=True, with_ingredient_ids=True, with_step_ids=True
                ),
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
        tags: [int,]
        steps: [
            {
                'order': int,
                'instruction': str,
                'recipe_id': (int, str)
            }
        ],
        ingredients: [
            {
                amount: decimal,
                unit: str,
                specifier: str,
                parent_recipe_id: int
                ingredient_id: int
            }
        ],
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
                recipe.to_json(
                    with_tag_ids=True, with_ingredient_ids=True, with_step_ids=True
                ),
                status=status.HTTP_200_OK,
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
                    with_tag_ids=True, with_ingredient_ids=True, with_step_ids=True
                ),
                status=status.HTTP_200_OK,
            )

        return response
