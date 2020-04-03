"""
Views for /ingredient/ and /ingredient/<pk>/
"""
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status
from .. import models, utils, constants

# pylint: disable=no-self-use
class IngredientView(APIView):
    """
    [GET, POST]: /ingredient/
    {id: int, name: str, recipe_id: (int, None)}
    """

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request):
        """Get list of all ingredients

        Args:
            request (HttpRequest): Django HttpRequest

        Returns:
            Response: DRF Response
        """
        return Response(
            tuple(
                ingredient.to_json() for ingredient in models.Ingredient.objects.all()
            ),
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        """Create new Ingredient

        Args:
            request (HttpRequest): Django HttpRequest

        Returns:
            Response: DRF Response
        """
        ingredient = request.data
        if errors := utils.validate_required_fields(
            ingredient, constants.REQUIRED_INGREDIENT_FIELDS
        ):
            return Response(
                {"message": " ".join(errors)}, status=status.HTTP_400_BAD_REQUEST,
            )

        ingredient, created = models.Ingredient.objects.get_or_create(
            name=ingredient["name"], defaults={"recipe_id": ingredient["recipe_id"]}
        )

        return Response(
            ingredient.to_json(),
            status=status.HTTP_201_CREATED if created else status.HTTP_409_CONFLICT,
        )


class IngredientDetailView(APIView):
    """
    [GET]: /ingredient/<int:pk>/
    {id: int, name: str, recipe_id: (int, None)}
    """

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, pk):
        """Get ingredient

        Args:
            request (HttpRequest): Django HttpRequest
            pk (str): ingredient primary key

        Returns:
            Response: DRF Response
        """
        try:
            ingredient = models.Ingredient.objects.get(id=pk)

        except models.Ingredient.DoesNotExist:
            response = Response(
                {"message": "No ingredient found with that ID"},
                status=status.HTTP_404_NOT_FOUND,
            )

        else:
            response = Response(ingredient.to_json(), status=status.HTTP_200_OK,)

        return response
