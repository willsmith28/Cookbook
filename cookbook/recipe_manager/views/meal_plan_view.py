"""
Views for /meal-plan/ and /meal-plan/<pk>/
"""
import datetime
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from ..serializers import MealPlanSerializer
from .. import models, utils, constants


class MealPlanView(APIView):
    """
    [GET, POST]: /meal-plan/
    {
        recipe_id: int,
        planned_date: str,
        meal: str,
        cooked: bool,
    }
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """Get users meal plans for authenticated user
        default behavior gets meal plans with dates greater than 4 days ago.
        provide historical = 1, true to get all meal plans for user

        Args:
            request (HttpRequest): Django HttpRequest

        Returns:
            Response: DRF Response
        """
        user = request.user
        query = {"user_id": user.id}

        if not request.query_params.get("historical", False):
            four_days_ago = datetime.date.today() - datetime.timedelta(days=4)
            query["planned_date__gt"] = four_days_ago

        return Response(
            tuple(
                MealPlanSerializer(meal_plan).data
                for meal_plan in models.MealPlan.objects.filter(**query)
            ),
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        """Create meal plan for logged in user

        Args:
            request (HttpRequest): Django HttpRequest

        Returns:
            Response: DRF Response
        """
        serializer = MealPlanSerializer(
            data={**request.data, "user_id": request.user.id}
        )

        if not serializer.is_valid():
            response = Response(
                {"errors": utils.serialize_errors(serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            serializer.save()
            response = Response(serializer.data, status.HTTP_201_CREATED)

        return response


class MealPlanDetailView(APIView):
    """
    PUT /meal-plan/<int:pk>/
    """

    def put(self, request, pk):
        """Edit Meal Plan

        Args:
            request ([type]): [description]
            pk ([type]): [description]
        """
        try:
            meal_plan = models.MealPlan.objects.get(id=pk)

        except models.MealPlan.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND,)

        if not utils.user_owns_item(
            meal_plan.user_id, request.user.id, request.user.is_superuser
        ):
            return constants.NOT_ALLOWED_RESPONSE

        serializer = MealPlanSerializer(meal_plan, data=request.data)

        if not serializer.is_valid():
            response = Response({"errors": utils.serialize_errors(serializer.errors)})

        else:
            serializer.save()
            response = Response(serializer.data, status=status.HTTP_200_OK)

        return response
