from unittest.mock import patch

import pytest
from rest_framework import status
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


class TestTruckSearchView:
    @patch("search.views.search_trucks")
    def test_returns_search_results(self, mock_search, api_client):
        mock_search.return_value = [
            {
                "db_id": 1,
                "applicant": "Taco Truck",
                "food_items": "Tacos",
                "facility_type": "Truck",
                "status": "APPROVED",
                "address": "123 Main St",
                "latitude": 37.7749,
                "longitude": -122.4194,
                "score": 9.5,
            }
        ]
        response = api_client.get("/api/v1/search/", {"q": "taco"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["applicant"] == "Taco Truck"

    def test_missing_query_param_returns_400(self, api_client):
        response = api_client.get("/api/v1/search/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data

    def test_blank_query_returns_400(self, api_client):
        response = api_client.get("/api/v1/search/", {"q": ""})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
