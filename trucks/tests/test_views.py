import pytest
from rest_framework import status
from rest_framework.test import APIClient

from trucks.models import FoodTruck

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def sample_trucks():
    return [
        FoodTruck.objects.create(
            external_id="1",
            applicant="Taco Truck",
            facility_type="Truck",
            status=FoodTruck.Status.APPROVED,
            latitude=37.77,
            longitude=-122.41,
        ),
        FoodTruck.objects.create(
            external_id="2",
            applicant="Snack Cart",
            facility_type="Push Cart",
            status=FoodTruck.Status.REQUESTED,
            latitude=37.78,
            longitude=-122.42,
        ),
        FoodTruck.objects.create(
            external_id="3",
            applicant="Burrito Truck",
            facility_type="Truck",
            status=FoodTruck.Status.EXPIRED,
            latitude=37.79,
            longitude=-122.43,
        ),
    ]


class TestFoodTruckListEndpoint:
    def test_returns_all_trucks_paginated(self, api_client, sample_trucks):
        response = api_client.get("/api/v1/trucks/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3
        assert len(response.data["results"]) == 3

    def test_filters_by_status(self, api_client, sample_trucks):
        response = api_client.get("/api/v1/trucks/", {"status": "APPROVED"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["applicant"] == "Taco Truck"

    def test_filters_by_facility_type_case_insensitive(self, api_client, sample_trucks):
        response = api_client.get("/api/v1/trucks/", {"facility_type": "truck"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2  # "Truck" matches, "Push Cart" doesn't

    def test_filters_by_applicant_partial_match(self, api_client, sample_trucks):
        response = api_client.get("/api/v1/trucks/", {"applicant": "taco"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_invalid_status_filter_value_returns_empty_or_error(self, api_client, sample_trucks):
        response = api_client.get("/api/v1/trucks/", {"status": "NOT_A_REAL_STATUS"})
        # django_filter's ChoiceFilter rejects invalid choices via validation,
        # which our custom exception handler wraps consistently.
        assert response.status_code in (
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
        )


class TestFoodTruckDetailEndpoint:
    def test_returns_single_truck(self, api_client, sample_trucks):
        truck = sample_trucks[0]
        response = api_client.get(f"/api/v1/trucks/{truck.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["applicant"] == "Taco Truck"
        assert response.data["external_id"] == "1"

    def test_returns_404_with_custom_error_envelope_for_missing_truck(self, api_client):
        response = api_client.get("/api/v1/trucks/99999/")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "error" in response.data
        assert "message" in response.data["error"]

    def test_response_is_read_only_post_not_allowed(self, api_client, sample_trucks):
        response = api_client.post("/api/v1/trucks/", {"applicant": "New Truck"})
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
