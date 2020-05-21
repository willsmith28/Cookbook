"""Get user view
"""
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class TokenObtainPairSerializerWithClaims(TokenObtainPairSerializer):
    """
    simple_jwt TokenObtainPairSerializer extension to add user info to jwt claims
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token["username"] = user.username
        token["email"] = user.email
        token["is_staff"] = user.is_staff
        token["is_superuser"] = user.is_superuser
        token["date_joined"] = user.date_joined.strftime("%Y-%m-%dT%H-%M-%S")

        return token


class TokenObtainPairViewWithClaims(TokenObtainPairView):
    """
    TokenObtainPairView extension to use custom Serializer
    """

    serializer_class = TokenObtainPairSerializerWithClaims
