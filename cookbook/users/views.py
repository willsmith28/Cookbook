"""Get user view
"""
import datetime
import os
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import TokenObtainPairSerializerWithClaims

SECURE_COOKIE = os.environ.get("APP_ENV", "dev").strip('"') == "prod"


class LogoutRemoveCookiesView(APIView):
    """
    provides route that removes cookies from request
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        /token/logout/
        """
        response = Response(status=status.HTTP_204_NO_CONTENT)
        _remove_cookies_from_response(response)

        return response


class TokenObtainPairWithCookiesView(TokenObtainPairView):
    """
    TokenObtainPairView extension to set cookies
    """

    serializer_class = TokenObtainPairSerializerWithClaims

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if all(field in response.data for field in ("access", "refresh")):
            _add_cookies_to_response(
                response, response.data["access"], response.data["refresh"]
            )

        else:
            response.delete_cookie("access")
            response.delete_cookie("refresh")

        return response


class TokenRefreshWithCookiesView(TokenRefreshView):
    """
    Override Token Refresh to prefer Cookies
    """

    serializer_class = TokenObtainPairSerializerWithClaims

    def post(self, request, *args, **kwargs):

        if (cookie_token := request.COOKIES.get("refresh", None)) is not None:
            request.data["refresh"] = cookie_token

        response = super().post(request, *args, **kwargs)

        if all(field in response.data for field in ("access", "refresh")):
            _add_cookies_to_response(
                response, response.data["access"], response.data["refresh"]
            )

        else:
            _remove_cookies_from_response(response)

        return response


def _add_cookies_to_response(response, access_token, refresh_token):
    now = datetime.datetime.utcnow()
    access_token_expires = now + settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]
    refresh_token_expires = now + settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]
    response.set_cookie(
        "access",
        value=f"Bearer {access_token}",
        httponly=True,
        samesite="Strict",
        secure=SECURE_COOKIE,
        expires=access_token_expires,
    )
    response.set_cookie(
        "refresh",
        value=refresh_token,
        httponly=True,
        samesite="Strict",
        secure=SECURE_COOKIE,
        expires=refresh_token_expires,
    )


def _remove_cookies_from_response(response):
    response.delete_cookie("access")
    response.delete_cookie("refresh")
