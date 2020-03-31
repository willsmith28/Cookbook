"""Test Django User api
"""
from django.test import TestCase
from django.urls import reverse
from . import models
from ..recipe_manager.tests import get_token

TEST_USER_NAME = "testUser"
TEST_EMAIL = "test@test.net"
TEST_PASSWORD = "abc123"


class UserTestCase(TestCase):
    """User tests
    """

    def setUp(self):
        models.User.objects.create_user(
            TEST_USER_NAME, email=TEST_EMAIL, password=TEST_PASSWORD
        )

    def test_login_token(self):
        """Test getting login token
        """
        response = self.client.post(
            "/api-token-auth/", {"username": TEST_USER_NAME, "password": TEST_PASSWORD}
        )
        response_json = response.json()
        self.assertIn("token", response_json)

    def test_get_user(self):
        """tests getting user information
        """
        token = get_token()
        response = self.client.get(
            reverse("user"),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {token}",
        )
        response_data = response.json()
        self.assertEqual(response_data["email"], TEST_EMAIL)
