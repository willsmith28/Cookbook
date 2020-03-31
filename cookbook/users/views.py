"""Get user view
"""
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


class UserView(APIView):
    """GET -> /me/
    """

    permissions = (IsAuthenticated,)

    def get(self, request):
        """
        Get Logged in user data
        """
        user = request.user
        return Response(user.to_json(), status=status.HTTP_200_OK)
