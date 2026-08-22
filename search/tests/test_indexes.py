from unittest.mock import Mock, patch

from elasticsearch.exceptions import NotFoundError

from search.indexes import create_index_if_not_exists, delete_index_if_exists


class TestCreateIndexIfNotExists:
    @patch("search.indexes.es_client")
    def test_creates_index_when_it_does_not_exist(self, mock_es_client):
        mock_es_client.indices.exists.return_value = False
        create_index_if_not_exists()
        mock_es_client.indices.create.assert_called_once()

    @patch("search.indexes.es_client")
    def test_does_not_recreate_index_when_it_already_exists(self, mock_es_client):
        mock_es_client.indices.exists.return_value = True
        create_index_if_not_exists()
        mock_es_client.indices.create.assert_not_called()


class TestDeleteIndexIfExists:
    @patch("search.indexes.es_client")
    def test_deletes_index_when_it_exists(self, mock_es_client):
        delete_index_if_exists()
        mock_es_client.indices.delete.assert_called_once()

    @patch("search.indexes.es_client")
    def test_silently_ignores_when_index_does_not_exist(self, mock_es_client):
        mock_es_client.indices.delete.side_effect = NotFoundError("index_not_found_exception", meta=Mock(), body={})
        # Should not raise — the function is designed to swallow this specific exception.
        delete_index_if_exists()
        mock_es_client.indices.delete.assert_called_once()
