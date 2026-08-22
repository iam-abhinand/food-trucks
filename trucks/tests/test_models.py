import pytest

from trucks.models import FoodTruck

pytestmark = pytest.mark.django_db


class TestFoodTruckStr:
    def test_str_returns_applicant_and_status(self):
        truck = FoodTruck.objects.create(
            external_id="1",
            applicant="Taco Truck",
            status=FoodTruck.Status.APPROVED,
            latitude=37.77,
            longitude=-122.41,
        )
        assert str(truck) == "Taco Truck (APPROVED)"
