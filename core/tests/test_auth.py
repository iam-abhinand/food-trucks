import pytest
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user(username="testuser", password="testpass123")


class TestTokenObtainView:
    def test_returns_tokens_for_valid_credentials(self, api_client, user):
        response = api_client.post(
            "/api/v1/auth/token/",
            {"username": "testuser", "password": "testpass123"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_rejects_invalid_credentials(self, api_client, user):
        response = api_client.post(
            "/api/v1/auth/token/",
            {"username": "testuser", "password": "wrongpassword"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestTokenRefreshView:
    def test_returns_new_access_token_for_valid_refresh_token(self, api_client, user):
        obtain_response = api_client.post(
            "/api/v1/auth/token/",
            {"username": "testuser", "password": "testpass123"},
        )
        refresh_token = obtain_response.data["refresh"]
        response = api_client.post(
            "/api/v1/auth/token/refresh/",
            {"refresh": refresh_token},
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

    def test_rejects_invalid_refresh_token(self, api_client):
        response = api_client.post(
            "/api/v1/auth/token/refresh/",
            {"refresh": "not-a-real-token"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
