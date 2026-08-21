import pytest

from search.documents import build_document
from trucks.models import FoodTruck

pytestmark = pytest.mark.django_db


class TestBuildDocument:
    def test_builds_correct_document_shape(self):
        truck = FoodTruck.objects.create(
            external_id="1",
            applicant="Taco Truck",
            facility_type="Truck",
            food_items="Tacos, Burritos",
            status=FoodTruck.Status.APPROVED,
            address="123 Main St",
            latitude=37.7749,
            longitude=-122.4194,
        )
        doc = build_document(truck)
        assert doc == {
            "db_id": truck.id,
            "applicant": "Taco Truck",
            "food_items": "Tacos, Burritos",
            "facility_type": "Truck",
            "status": "APPROVED",
            "address": "123 Main St",
            "latitude": 37.7749,
            "longitude": -122.4194,
        }
