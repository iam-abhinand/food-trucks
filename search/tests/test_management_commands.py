from io import StringIO
from unittest.mock import patch

import pytest
from django.core.management import call_command

pytestmark = pytest.mark.django_db


class TestIndexTrucksCommand:
    @patch("search.management.commands.index_trucks.bulk_index_trucks")
    @patch("search.management.commands.index_trucks.create_index_if_not_exists")
    def test_creates_index_and_bulk_indexes(self, mock_create_index, mock_bulk_index):
        mock_bulk_index.return_value = (497, 0)
        out = StringIO()
        call_command("index_trucks", stdout=out)
        mock_create_index.assert_called_once()
        mock_bulk_index.assert_called_once()
        assert "Indexed 497 trucks" in out.getvalue()

    @patch("search.management.commands.index_trucks.bulk_index_trucks")
    @patch("search.management.commands.index_trucks.create_index_if_not_exists")
    def test_reports_errors_in_output(self, mock_create_index, mock_bulk_index):
        mock_bulk_index.return_value = (490, 7)
        out = StringIO()
        call_command("index_trucks", stdout=out)
        assert "490 trucks" in out.getvalue()
        assert "7 errors" in out.getvalue()
