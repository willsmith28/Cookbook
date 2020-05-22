"""
app authentication
"""
from rest_framework_simplejwt.authentication import JWTAuthentication


class JWTCookieAuthentication(JWTAuthentication):
    """
    Override JWTAuthentication to prefer cookies if provided
    """

    def get_header(self, request):
        cookie_token = request.COOKIES.get("access", None)

        return cookie_token if cookie_token is not None else super().get_header(request)
