from io import StringIO
from unittest.mock import patch

import pytest
from django.core.management import call_command

pytestmark = pytest.mark.django_db


class TestSyncFoodTrucksCommand:
    @patch("ingestion.management.commands.sync_food_trucks.sync_food_trucks")
    def test_calls_sync_task_with_default_limit(self, mock_sync_task):
        mock_sync_task.return_value = {
            "total_fetched": 10,
            "created": 10,
            "updated": 0,
            "skipped": 0,
            "index_errors": 0,
        }
        out = StringIO()
        call_command("sync_food_trucks", stdout=out)
        mock_sync_task.assert_called_once_with(limit=1000)
        assert "Sync complete" in out.getvalue()
        assert "10 created" in out.getvalue()

    @patch("ingestion.management.commands.sync_food_trucks.sync_food_trucks")
    def test_respects_custom_limit_argument(self, mock_sync_task):
        mock_sync_task.return_value = {
            "total_fetched": 5,
            "created": 5,
            "updated": 0,
            "skipped": 0,
            "index_errors": 0,
        }
        out = StringIO()
        call_command("sync_food_trucks", "--limit", "5", stdout=out)
        mock_sync_task.assert_called_once_with(limit=5)
