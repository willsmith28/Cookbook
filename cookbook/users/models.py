"""Django Base User
"""
from django.db import models
from django.contrib.auth import models as auth_models
from django.utils import timezone


class User(auth_models.AbstractBaseUser, auth_models.PermissionsMixin):
    """User for this site

    Args:
        username (str): unique username
        email (str): unique email
        is_staff (bool): controls admin login
        is_superuser (bool): controls superuser permission
        date_joined (datetime): date account was created
    """

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = auth_models.UserManager()

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ("email",)

    class Meta:
        db_table = "cookbook_user"
