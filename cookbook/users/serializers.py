from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


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
