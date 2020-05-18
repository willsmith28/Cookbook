"""
Views for /recipe/<recipe_pk>/steps/ and /recipe/<recipe_pk>/steps/<step_pk>
"""

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status
from ..serializers import StepSerializer
from .. import models, utils, constants


class RecipeStep(APIView):
    """
    [GET, POST] /recipe/<int:recipe_pk>/steps/
    {
        id: int,
        order: int,
        instruction: str,
        recipe_id: int
    }
    only instruction is required to post
    Args:
        APIView ([type]): [description]
    """

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, recipe_pk):
        """Get list of steps in the recipe

        Args:
            request (HttpRequest): Django HttpRequest
            recipe_pk (int): Recipe primary key

        Returns
            Response: DRF response
        """
        try:
            recipe = models.Recipe.objects.prefetch_related("steps").get(id=recipe_pk)

        except models.Recipe.DoesNotExist:
            response = Response(status=status.HTTP_404_NOT_FOUND,)

        else:
            response = Response(
                tuple(StepSerializer(step).data for step in recipe.steps.all()),
                status=status.HTTP_200_OK,
            )

        return response

    def post(self, request, recipe_pk):
        """Create new step

        Args:
            request (HttpRequest): Django HttpRequest
            recipe_pk (int): Recipe primary key

        Returns
            Response: DRF response
        """
        try:
            recipe = models.Recipe.objects.get(id=recipe_pk)

        except models.Recipe.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND,)

        if not utils.user_owns_item(
            recipe.author_id, request.user.id, request.user.is_superuser
        ):
            return constants.NOT_ALLOWED_RESPONSE

        current_step_count = recipe.steps.count()
        serializer = StepSerializer(
            data={
                **request.data,
                "recipe_id": recipe_pk,
                "order": current_step_count + 1,
            }
        )

        if not serializer.is_valid():
            response = Response(
                {"errors": utils.serialize_errors(serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            serializer.save()
            response = Response(serializer.data, status=status.HTTP_201_CREATED)

        return response


class RecipeStepDetail(APIView):
    """
    [GET, PUT, DELETE] /recipe/<int:recipe_pk>/steps/<int:order>/
    {
        id: int,
        order: int,
        instruction: str,
        recipe_id: int
    }
    """

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, recipe_pk, order):
        """get step detail

        Args:
            request (HttpRequest): Django HttpRequest
            recipe_pk (int): Recipe primary key
            step_pk (int): Step primary key

        Returns
            Response: DRF response
        """
        try:
            step = models.Step.objects.get(recipe_id=recipe_pk, order=order)

        except models.Step.DoesNotExist:
            response = Response(status=status.HTTP_404_NOT_FOUND,)

        else:
            response = Response(StepSerializer(step).data, status=status.HTTP_200_OK)

        return response

    def put(self, request, recipe_pk, order):
        """edit a step

        Args:
            request (HttpRequest): Django HttpRequest
            recipe_pk (int): Recipe primary key
            step_pk (int): Step primary key

        Returns
            Response: DRF response
        """
        try:
            step = models.Step.objects.select_related("recipe").get(
                recipe_id=recipe_pk, order=order
            )

        except models.Step.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND,)

        if not utils.user_owns_item(
            step.recipe.author_id, request.user.id, request.user.is_superuser
        ):
            return constants.NOT_ALLOWED_RESPONSE

        serializer = StepSerializer(step, data={**request.data, "order": step.order})

        if not serializer.is_valid():
            response = Response({"errors": utils.serialize_errors(serializer.errors)})
        else:
            serializer.save()
            response = Response(serializer.data, status=status.HTTP_200_OK)

        return response

    def delete(self, request, recipe_pk, order):
        """Delete Step

        Args:
            request (HttpRequest): Django HttpRequest
            recipe_pk (int): Recipe primary key
            step_pk (int): Step primary key

        Returns
            Response: DRF response
        """
        try:
            step = models.Step.objects.select_related("recipe").get(
                recipe_id=recipe_pk, order=order
            )

        except models.Step.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND,)

        if not utils.user_owns_item(
            step.recipe.author_id, request.user.id, request.user.is_superuser
        ):
            return constants.NOT_ALLOWED_RESPONSE

        if models.Step.objects.filter(recipe_id=recipe_pk).count() == step.order:
            step.delete()
            response = Response(status=status.HTTP_204_NO_CONTENT)

        else:
            response = Response(
                {"errors": ("Steps must be deleted in decresing order",)},
                status=status.HTTP_409_CONFLICT,
            )

        return response
