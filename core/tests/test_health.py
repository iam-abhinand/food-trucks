from unittest.mock import patch

import pytest
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


class TestHealthCheckView:
    def test_returns_200_when_all_dependencies_healthy(self, api_client):
        response = api_client.get("/health/")
        assert response.status_code == 200
        assert response.data["status"] == "healthy"
        assert response.data["checks"]["database"] is True
        assert response.data["checks"]["cache"] is True

    @patch("core.views.HealthCheckView._check_elasticsearch")
    def test_returns_503_when_elasticsearch_down(self, mock_es_check, api_client):
        mock_es_check.return_value = False
        response = api_client.get("/health/")
        assert response.status_code == 503
        assert response.data["status"] == "unhealthy"
        assert response.data["checks"]["elasticsearch"] is False

    @patch("core.views.HealthCheckView._check_database")
    def test_returns_503_when_database_down(self, mock_db_check, api_client):
        mock_db_check.return_value = False
        response = api_client.get("/health/")
        assert response.status_code == 503
        assert response.data["checks"]["database"] is False

    def test_does_not_require_authentication(self, api_client):
        # No force_authenticate call — confirms this endpoint is public
        response = api_client.get("/health/")
        assert response.status_code in (200, 503)  # never 401/403
