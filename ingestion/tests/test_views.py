from unittest.mock import patch

import pytest
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.throttling import ScopedRateThrottle

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user(username="testuser", password="testpass123")


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


class TestTriggerSyncView:
    def test_rejects_unauthenticated_requests(self, api_client):
        response = api_client.post("/api/v1/sync/", {"limit": 5})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch("ingestion.views.sync_food_trucks")
    def test_authenticated_request_triggers_task(self, mock_sync_task, authenticated_client):
        mock_task_result = type("MockTask", (), {"id": "fake-task-id-123"})()
        mock_sync_task.delay.return_value = mock_task_result
        response = authenticated_client.post("/api/v1/sync/", {"limit": 5})
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.data["task_id"] == "fake-task-id-123"
        mock_sync_task.delay.assert_called_once_with(limit=5)

    @patch("ingestion.views.sync_food_trucks")
    def test_defaults_to_limit_1000_when_not_provided(self, mock_sync_task, authenticated_client):
        mock_task_result = type("MockTask", (), {"id": "fake-task-id-456"})()
        mock_sync_task.delay.return_value = mock_task_result
        authenticated_client.post("/api/v1/sync/", {})
        mock_sync_task.delay.assert_called_once_with(limit=1000)


class TestTriggerSyncThrottling:
    @patch("ingestion.views.sync_food_trucks")
    def test_throttles_after_exceeding_scoped_rate(self, mock_sync_task, authenticated_client, monkeypatch):
        monkeypatch.setitem(ScopedRateThrottle.THROTTLE_RATES, "sync", "2/minute")
        mock_task_result = type("MockTask", (), {"id": "fake-id"})()
        mock_sync_task.delay.return_value = mock_task_result

        # First 2 requests should succeed (within the 2/minute limit)
        for _ in range(2):
            response = authenticated_client.post("/api/v1/sync/", {"limit": 5})
            assert response.status_code == status.HTTP_202_ACCEPTED

        # 3rd request should be throttled
        response = authenticated_client.post("/api/v1/sync/", {"limit": 5})
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
