import pytest
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APIClient

from trucks.models import FoodTruck

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def clear_cache():
    """Ensure Redis cache doesn't leak results between tests."""
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def trucks_near_ferry_building():
    """
    Ferry Building, SF: (37.7955, -122.3937)
    One truck very close, one moderately far, one far outside any reasonable radius.
    """
    close_truck = FoodTruck.objects.create(
        external_id="close",
        applicant="Close Truck",
        status=FoodTruck.Status.APPROVED,
        latitude=37.7960,  # ~60m away
        longitude=-122.3940,
    )
    mid_truck = FoodTruck.objects.create(
        external_id="mid",
        applicant="Mid Truck",
        status=FoodTruck.Status.APPROVED,
        latitude=37.8044,  # roughly 1-2km away
        longitude=-122.2712,
    )
    far_truck = FoodTruck.objects.create(
        external_id="far",
        applicant="Far Truck",
        status=FoodTruck.Status.APPROVED,
        latitude=34.0522,  # Los Angeles — very far
        longitude=-118.2437,
    )
    return close_truck, mid_truck, far_truck


class TestNearbyEndpoint:
    def test_returns_only_trucks_within_radius(
        self, api_client, trucks_near_ferry_building
    ):
        response = api_client.get(
            "/api/v1/trucks/nearby/",
            {"lat": 37.7955, "lng": -122.3937, "radius_km": 1},
        )
        assert response.status_code == status.HTTP_200_OK
        applicants = [truck["applicant"] for truck in response.data]
        assert "Close Truck" in applicants
        assert "Far Truck" not in applicants

    def test_results_sorted_by_distance_ascending(
        self, api_client, trucks_near_ferry_building
    ):
        response = api_client.get(
            "/api/v1/trucks/nearby/",
            {"lat": 37.7955, "lng": -122.3937, "radius_km": 50},
        )
        distances = [truck["distance_km"] for truck in response.data]
        assert distances == sorted(distances)

    def test_missing_required_params_returns_400(self, api_client):
        response = api_client.get("/api/v1/trucks/nearby/", {"lat": 37.7955})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data

    def test_out_of_range_latitude_returns_400(self, api_client):
        response = api_client.get(
            "/api/v1/trucks/nearby/",
            {"lat": 999, "lng": -122.3937},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_radius_defaults_when_not_provided(
        self, api_client, trucks_near_ferry_building
    ):
        response = api_client.get(
            "/api/v1/trucks/nearby/",
            {"lat": 37.7955, "lng": -122.3937},
        )
        # default radius_km=2.0 should still include the close truck
        assert response.status_code == status.HTTP_200_OK
        applicants = [truck["applicant"] for truck in response.data]
        assert "Close Truck" in applicants

    def test_each_result_includes_distance_km(
        self, api_client, trucks_near_ferry_building
    ):
        response = api_client.get(
            "/api/v1/trucks/nearby/",
            {"lat": 37.7955, "lng": -122.3937, "radius_km": 1},
        )
        for truck in response.data:
            assert "distance_km" in truck
            assert isinstance(truck["distance_km"], float)
