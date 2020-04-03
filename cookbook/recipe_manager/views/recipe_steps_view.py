
"""
Views for /recipe/<recipe_pk>/steps/ and /recipe/<recipe_pk>/steps/<step_pk>
"""
from django.db import IntegrityError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status
from .. import models


class RecipeStep(APIView):
    """
    [GET, POST] /recipe/<int:recipe_pk>/steps/
    {
        id: int,
        order: int,
        instruction: str,
        recipe_id: int
    }
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
            response = Response(
                {"message": "Recipe with that id not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        else:
            response = Response(
                tuple(step.to_json() for step in recipe.steps.all()),
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
            return Response(
                {"message": "Recipe with that id not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user.id != recipe.author_id:
            if not request.user.is_superuser:
                return Response(
                    {"message": "Cannot edit a recipe that is not yours"},
                    status=status.HTTP_403_FORBIDDEN,
                )

        step = request.data
        current_step_count = recipe.steps.count()

        try:
            step = recipe.steps.create(
                instruction=step["instruction"], order=current_step_count + 1
            )

        except IntegrityError as err:
            response = Response(
                {"message": str(err.__cause__)}, status=status.HTTP_400_BAD_REQUEST
            )

        except KeyError:
            response = Response(
                {"message": "instruction is a required field"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        else:
            response = Response(step.to_json(), status=status.HTTP_201_CREATED)

        return response


class RecipeStepDetail(APIView):
    """
    [GET, PUT, DELETE] /recipe/<int:recipe_pk>/steps/<int:step_pk>/
    {
        id: int,
        order: int,
        instruction: str,
        recipe_id: int
    }
    """

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, recipe_pk, step_pk):
        """get step detail

        Args:
            request (HttpRequest): Django HttpRequest
            recipe_pk (int): Recipe primary key
            step_pk (int): Step primary key

        Returns
            Response: DRF response
        """
        try:
            models.Recipe.objects.values("id").get(id=recipe_pk)
            step = models.Step.objects.get(id=step_pk)

        except models.Recipe.DoesNotExist:
            response = Response(
                {"message": "Recipe with that id not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        except models.Step.DoesNotExist:
            response = Response(
                {"message": "Step with that id not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        else:
            response = Response(step.to_json(), status=status.HTTP_200_OK)

        return response

    def put(self, request, recipe_pk, step_pk):
        """edit a step

        Args:
            request (HttpRequest): Django HttpRequest
            recipe_pk (int): Recipe primary key
            step_pk (int): Step primary key

        Returns
            Response: DRF response
        """
        try:
            recipe = models.Recipe.objects.values("author_id").get(id=recipe_pk)
            step = models.Step.objects.get(id=step_pk)

        except models.Recipe.DoesNotExist:
            return Response(
                {"message": "Recipe with that id not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        except models.Step.DoesNotExist:
            return Response(
                {"message": "Recipe with that id not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user.id != recipe["author_id"]:
            if not request.user.is_superuser:
                return Response(
                    {"message": "Cannot edit a recipe that is not yours"},
                    status=status.HTTP_403_FORBIDDEN,
                )

        try:
            if (instruction := request.data["instruction"]) != step.instruction:
                step.instruction = instruction
                step.save()

        except IntegrityError as err:
            response = Response(
                {"message": str(err.__cause__)}, status=status.HTTP_400_BAD_REQUEST
            )

        except KeyError:
            response = Response(
                {"message": "instruction is a required field."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        else:
            response = Response(step.to_json(), status=status.HTTP_200_OK)

        return response

    def delete(self, request, recipe_pk, step_pk):
        """Delete Step

        Args:
            request (HttpRequest): Django HttpRequest
            recipe_pk (int): Recipe primary key
            step_pk (int): Step primary key

        Returns
            Response: DRF response
        """
        try:
            recipe = models.Recipe.objects.get(id=recipe_pk)
            step = models.Step.objects.get(id=step_pk)

        except models.Recipe.DoesNotExist:
            return Response(
                {"message": "Recipe with that id not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        except models.Step.DoesNotExist:
            return Response(
                {"message": "Recipe with that id not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user.id != recipe.author_id:
            if not request.user.is_superuser:
                return Response(
                    {"message": "Cannot edit a recipe that is not yours"},
                    status=status.HTTP_403_FORBIDDEN,
                )

        if recipe.steps.count() == step.order:
            step.delete()
            response = Response(status=status.HTTP_204_NO_CONTENT)

        else:
            response = Response(
                {"message": "Steps must be deleted in decresing order"},
                status=status.HTTP_409_CONFLICT,
            )

        return response
