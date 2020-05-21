"""Get user view
"""
import datetime
import os
from django.conf import settings
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

SECURE_COOKIE = os.environ.get("APP_ENV", "dev").strip('"') == "prod"


class TokenObtainPairWithCookiesView(TokenObtainPairView):
    """
    TokenObtainPairView extension to set cookies
    """

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if "access" in response.data and "refresh" in response.data:
            access_token = response.data["access"]
            refresh_token = response.data["refresh"]
            response = _add_cookies_to_response(response, access_token, refresh_token)

        else:
            response.delete_cookie("access")
            response.delete_cookie("refresh")

        return response


class TokenRefreshWithCookiesView(TokenRefreshView):
    """
    Override Token Refresh to prefer Cookies
    """

    def post(self, request, *args, **kwargs):
        cookie_token = request.COOKIES.get("refresh", None)
        if cookie_token is not None:
            request.data["refresh"] = cookie_token

        response = super().post(request, *args, **kwargs)

        if "access" in response.data and "refresh" in response.data:
            access_token = response.data["access"]
            refresh_token = response.data["refresh"]
            response = _add_cookies_to_response(response, access_token, refresh_token)

        else:
            response.delete_cookie("access")
            response.delete_cookie("refresh")

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

    return response
