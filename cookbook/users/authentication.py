"""
app authentication
"""
from rest_framework_simplejwt.authentication import JWTAuthentication


class JWTCookieAuthentication(JWTAuthentication):
    """
    Override JWTAuthentication to prefer cookies if provided
    """

    def get_header(self, request):
        token = None
        header_token = super().get_header(request)
        cookie_token = request.COOKIES.get("access", None)

        if cookie_token is not None:
            token = cookie_token
        elif header_token is not None:
            token = header_token

        return token
