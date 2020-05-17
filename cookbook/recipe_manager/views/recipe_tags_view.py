"""
Views for /recipe/<recipe_pk>/tags/ and /recipe/<recipe_pk>/tags/<step_pk>
"""
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status
from ..serializers import TagSerializer
from .. import models, utils, constants


class RecipeTag(APIView):
    """
    [GET, POST] /recipe/<int:recipe_pk>/tags/
    {
        id: int,
        value: str
    }
    """

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, recipe_pk):
        """Get all tags on this recipe

        Args:
            request (HttpRequest): Django HttpRequest
            recipe_pk (int): Recipe primary key

        Returns:
            Response: DRF response
        """

        try:
            recipe = models.Recipe.objects.prefetch_related("tags").get(id=recipe_pk)

        except models.Recipe.DoesNotExist:
            response = Response(
                {"message": "Recipe with that id not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        else:
            response = Response(
                tuple(TagSerializer(tag).data for tag in recipe.tags.all()),
                status=status.HTTP_200_OK,
            )

        return response

    def post(self, request, recipe_pk):
        """Add new tag to this recipe

        Args:
            request (HttpRequest): Django HttpRequest
            recipe_pk (int): Recipe primary key

        Returns:
            Response: DRF response
        """
        try:
            recipe = models.Recipe.objects.prefetch_related("tags").get(id=recipe_pk)
            tag = models.Tag.objects.get(id=request.data["id"])

        except models.Recipe.DoesNotExist:
            return Response(
                {"message": "Recipe with that id was not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        except models.Tag.DoesNotExist:
            return Response(
                {"message": "Tag Id provided is invalid"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except KeyError:
            return Response(
                {"errors": {"id": ["This field is required"]}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not utils.user_owns_item(
            recipe.author_id, request.user.id, request.user.is_superuser
        ):
            return constants.NOT_ALLOWED_RESPONSE

        recipe.tags.add(tag)

        return Response(TagSerializer(tag).data, status=status.HTTP_201_CREATED)


class RecipeTagDelete(APIView):
    """
    [DELETE] /recipe/<int:recipe_pk>/tags/<tag_pk>/
    """

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def delete(self, request, recipe_pk, tag_pk):
        """Remove a tag from a recipe

        Args:
            request (HttpRequest): Django HttpRequest
            recipe_pk (int): Recipe primary key
            tag_pk (int): Tag primary key

        Returns:
            Response: DRF response
        """
        try:
            recipe = models.Recipe.objects.prefetch_related("tags").get(id=recipe_pk)
            tag = models.Tag.objects.get(id=tag_pk)

        except models.Recipe.DoesNotExist:
            return Response(
                {"message": "Recipe with that id was not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        except models.Tag.DoesNotExist:
            return Response(
                {"message": "Tag with that id was not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not utils.user_owns_item(
            recipe.author_id, request.user.id, request.user.is_superuser
        ):
            return constants.NOT_ALLOWED_RESPONSE

        recipe.tags.remove(tag)

        return Response(status=status.HTTP_204_NO_CONTENT)
