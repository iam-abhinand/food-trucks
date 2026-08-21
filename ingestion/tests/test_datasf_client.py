from unittest.mock import Mock, patch

import pytest
import requests

from ingestion.datasf_client import DataSFClientError, fetch_food_trucks


class TestFetchFoodTrucks:
    @patch("ingestion.datasf_client.requests.get")
    def test_returns_parsed_json_on_success(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = [{"objectid": "1"}, {"objectid": "2"}]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        result = fetch_food_trucks(limit=10)
        assert result == [{"objectid": "1"}, {"objectid": "2"}]
        mock_get.assert_called_once()

    @patch("ingestion.datasf_client.requests.get")
    def test_raises_client_error_on_network_failure(self, mock_get):
        mock_get.side_effect = requests.ConnectionError("connection refused")
        with pytest.raises(DataSFClientError):
            fetch_food_trucks()

    @patch("ingestion.datasf_client.requests.get")
    def test_raises_client_error_on_http_error_status(self, mock_get):
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("500 error")
        mock_get.return_value = mock_response
        with pytest.raises(DataSFClientError):
            fetch_food_trucks()

    @patch("ingestion.datasf_client.requests.get")
    def test_raises_client_error_on_invalid_json(self, mock_get):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = ValueError("invalid json")
        mock_get.return_value = mock_response
        with pytest.raises(DataSFClientError):
            fetch_food_trucks()
