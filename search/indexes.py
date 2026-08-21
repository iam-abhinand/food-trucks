"""
Elasticsearch index definition for food trucks.

Uses an edge_ngram analyzer on searchable text fields so partial, in-progress
queries (e.g. "tac") match complete words (e.g. "Tacos") — this is what
powers autocomplete-style search.
"""

import logging

from elasticsearch.exceptions import NotFoundError

from .es_client import es_client

logger = logging.getLogger(__name__)

INDEX_NAME = "food_trucks"

INDEX_SETTINGS = {
    "settings": {
        "analysis": {
            "filter": {
                "autocomplete_filter": {
                    "type": "edge_ngram",
                    "min_gram": 2,
                    "max_gram": 20,
                }
            },
            "analyzer": {
                "autocomplete_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "autocomplete_filter"],
                },
                "autocomplete_search_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase"],
                },
            },
        }
    },
    "mappings": {
        "properties": {
            "db_id": {"type": "integer"},
            "applicant": {
                "type": "text",
                "analyzer": "autocomplete_analyzer",
                "search_analyzer": "autocomplete_search_analyzer",
            },
            "food_items": {
                "type": "text",
                "analyzer": "autocomplete_analyzer",
                "search_analyzer": "autocomplete_search_analyzer",
            },
            "facility_type": {"type": "keyword"},
            "status": {"type": "keyword"},
            "address": {"type": "text"},
            "latitude": {"type": "float"},
            "longitude": {"type": "float"},
        }
    },
}


def create_index_if_not_exists():
    if not es_client.indices.exists(index=INDEX_NAME):
        es_client.indices.create(index=INDEX_NAME, body=INDEX_SETTINGS)
        logger.info("Created Elasticsearch index", extra={"index": INDEX_NAME})
    else:
        logger.info("Elasticsearch index already exists", extra={"index": INDEX_NAME})


def delete_index_if_exists():
    try:
        es_client.indices.delete(index=INDEX_NAME)
        logger.info("Deleted Elasticsearch index", extra={"index": INDEX_NAME})
    except NotFoundError:
        pass
