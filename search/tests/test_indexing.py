from unittest.mock import patch

import pytest

from search.indexing import bulk_index_trucks
from trucks.models import FoodTruck

pytestmark = pytest.mark.django_db


def _create_truck(external_id):
    return FoodTruck.objects.create(
        external_id=external_id,
        applicant=f"Truck {external_id}",
        status=FoodTruck.Status.APPROVED,
        latitude=37.77,
        longitude=-122.41,
    )


class TestBulkIndexTrucks:
    @patch("search.indexing.bulk")
    def test_indexes_all_trucks_when_no_queryset_given(self, mock_bulk):
        _create_truck("1")
        _create_truck("2")
        mock_bulk.return_value = (2, [])
        success_count, error_count = bulk_index_trucks()
        assert success_count == 2
        assert error_count == 0
        mock_bulk.assert_called_once()

    @patch("search.indexing.bulk")
    def test_indexes_only_given_queryset_when_provided(self, mock_bulk):
        _create_truck("1")
        _create_truck("2")
        mock_bulk.return_value = (1, [])
        subset = FoodTruck.objects.filter(external_id="1")
        success_count, error_count = bulk_index_trucks(queryset=subset)
        assert success_count == 1
        assert error_count == 0

    @patch("search.indexing.bulk")
    def test_returns_error_count_from_bulk_errors(self, mock_bulk):
        _create_truck("1")
        mock_bulk.return_value = (0, [{"index": {"error": "some_error"}}])
        success_count, error_count = bulk_index_trucks()
        assert success_count == 0
        assert error_count == 1
