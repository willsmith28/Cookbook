"""
app authentication
"""
from rest_framework import HTTP_HEADER_ENCODING
from rest_framework_simplejwt.authentication import JWTAuthentication


class JWTCookieAuthentication(JWTAuthentication):
    """
    Override JWTAuthentication to prefer cookies if provided
    """

    def get_header(self, request):
        cookie_token = request.COOKIES.get("access")

        return (
            cookie_token.encode(HTTP_HEADER_ENCODING)
            if cookie_token
            else super().get_header(request)
        )
