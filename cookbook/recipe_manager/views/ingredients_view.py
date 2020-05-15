"""
Views for /ingredient/ and /ingredient/<pk>/
"""
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import api_view
from rest_framework import status
from django.db import IntegrityError
from ..serializers import IngredientSerializer
from .. import models

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
                IngredientSerializer(ingredient).data
                for ingredient in models.Ingredient.objects.all()
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
        serializer = IngredientSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "errors": {
                        key: tuple(str(error) for error in errors)
                        for key, errors in serializer.errors.items()
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            serializer.save()
            response = Response(serializer.data, status=status.HTTP_201_CREATED)

        except IntegrityError as err:
            response = Response(
                {"message": str(err.__cause__)}, status=status.HTTP_400_BAD_REQUEST
            )

        return response


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
            response = Response(
                IngredientSerializer(ingredient).data, status=status.HTTP_200_OK,
            )

        return response


@api_view(["GET"])
def ingredient_units(request):
    """returns choices for ingredient units

    Args:
        request (HttpRequest): Django HttpRequest

    Returns:
        Response: DRF Response
    """
    return Response(models.IngredientInRecipe.UNITS, status=status.HTTP_200_OK)
