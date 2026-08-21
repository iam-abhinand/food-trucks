from unittest.mock import patch

import pytest

from ingestion.tasks import sync_food_trucks
from trucks.models import FoodTruck

pytestmark = pytest.mark.django_db


def _raw_record(objectid="1"):
    return {
        "objectid": objectid,
        "applicant": "Test Truck",
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


class TestSyncFoodTrucksIndexing:
    @patch("ingestion.tasks.index_truck")
    @patch("ingestion.tasks.fetch_food_trucks")
    def test_indexes_each_synced_truck(self, mock_fetch, mock_index_truck):
        mock_fetch.return_value = [_raw_record()]
        sync_food_trucks(limit=10)
        assert mock_index_truck.call_count == 1

    @patch("ingestion.tasks.index_truck")
    @patch("ingestion.tasks.fetch_food_trucks")
    def test_sync_succeeds_even_if_indexing_fails(self, mock_fetch, mock_index_truck):
        mock_fetch.return_value = [_raw_record()]
        mock_index_truck.side_effect = Exception("ES is down")
        result = sync_food_trucks(limit=10)
        # DB write still succeeded despite the ES failure
        assert result["created"] == 1
        assert result["index_errors"] == 1
        assert FoodTruck.objects.count() == 1
