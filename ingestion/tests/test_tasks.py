from unittest.mock import patch

import pytest

from ingestion.datasf_client import DataSFClientError
from ingestion.tasks import sync_food_trucks
from trucks.models import FoodTruck

pytestmark = pytest.mark.django_db


def _raw_record(objectid="1", applicant="Test Truck"):
    return {
        "objectid": objectid,
        "applicant": applicant,
        "facilitytype": "Truck",
        "address": "123 Main St",
        "permit": "PERMIT-1",
        "status": "APPROVED",
        "fooditems": "tacos",
        "latitude": "37.77",
        "longitude": "-122.41",
        "schedule": "",
        "expirationdate": "",
    }


class TestSyncFoodTrucks:
    @patch("ingestion.tasks.fetch_food_trucks")
    def test_creates_new_truck_on_first_sync(self, mock_fetch):
        mock_fetch.return_value = [_raw_record(objectid="1")]
        result = sync_food_trucks(limit=10)
        assert result == {
            "total_fetched": 1,
            "created": 1,
            "updated": 0,
            "skipped": 0,
            "index_errors": 0,
        }
        assert FoodTruck.objects.count() == 1
        assert FoodTruck.objects.get(external_id="1").applicant == "Test Truck"

    @patch("ingestion.tasks.fetch_food_trucks")
    def test_updates_existing_truck_on_second_sync(self, mock_fetch):
        mock_fetch.return_value = [_raw_record(objectid="1", applicant="Original Name")]
        sync_food_trucks(limit=10)
        mock_fetch.return_value = [_raw_record(objectid="1", applicant="Renamed Truck")]
        result = sync_food_trucks(limit=10)
        assert result == {
            "total_fetched": 1,
            "created": 0,
            "updated": 1,
            "skipped": 0,
            "index_errors": 0,
        }
        assert FoodTruck.objects.count() == 1
        assert FoodTruck.objects.get(external_id="1").applicant == "Renamed Truck"

    @patch("ingestion.tasks.fetch_food_trucks")
    def test_skips_unmappable_records_without_failing_whole_sync(self, mock_fetch):
        good_record = _raw_record(objectid="1")
        bad_record = _raw_record(objectid="2")
        del bad_record["latitude"]  # will make the mapper return None
        mock_fetch.return_value = [good_record, bad_record]
        result = sync_food_trucks(limit=10)
        assert result == {
            "total_fetched": 2,
            "created": 1,
            "updated": 0,
            "skipped": 1,
            "index_errors": 0,
        }
        assert FoodTruck.objects.count() == 1

    @patch("ingestion.tasks.fetch_food_trucks")
    def test_raises_retry_when_datasf_fetch_fails(self, mock_fetch):
        mock_fetch.side_effect = DataSFClientError("network down")
        # sync_food_trucks calls self.retry(), which raises a Retry exception
        # when the task isn't running under a real worker/broker context.
        with pytest.raises(Exception):  # noqa: B017
            sync_food_trucks(limit=10)
