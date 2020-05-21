"""User urls
"""
from django.urls import path
from . import views

urlpatterns = [
    path(
        "token/",
        views.TokenObtainPairWithCookiesView.as_view(),
        name="token_obtain_pair",
    ),
    path(
        "token/refresh/",
        views.TokenRefreshWithCookiesView.as_view(),
        name="token_refresh",
    ),
]
