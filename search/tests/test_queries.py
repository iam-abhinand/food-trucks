from unittest.mock import patch

from search.queries import search_trucks


class TestSearchTrucks:
    @patch("search.queries.es_client")
    def test_returns_mapped_hits_with_score(self, mock_es_client):
        mock_es_client.search.return_value = {
            "hits": {
                "hits": [
                    {
                        "_score": 9.5,
                        "_source": {
                            "db_id": 1,
                            "applicant": "Taco Truck",
                            "food_items": "Tacos",
                            "facility_type": "Truck",
                            "status": "APPROVED",
                            "address": "123 Main St",
                            "latitude": 37.7749,
                            "longitude": -122.4194,
                        },
                    }
                ]
            }
        }
        results = search_trucks("taco")
        assert len(results) == 1
        assert results[0]["applicant"] == "Taco Truck"
        assert results[0]["score"] == 9.5

    @patch("search.queries.es_client")
    def test_returns_empty_list_when_no_hits(self, mock_es_client):
        mock_es_client.search.return_value = {"hits": {"hits": []}}
        results = search_trucks("nonexistent query xyz")
        assert results == []

    @patch("search.queries.es_client")
    def test_boosts_applicant_field_in_query(self, mock_es_client):
        mock_es_client.search.return_value = {"hits": {"hits": []}}
        search_trucks("taco")
        call_args = mock_es_client.search.call_args
        query_body = call_args.kwargs["body"]
        assert "applicant^2" in query_body["query"]["multi_match"]["fields"]
