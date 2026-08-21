"""
Functions to write FoodTruck data into Elasticsearch.
"""

import logging

from elasticsearch.helpers import bulk

from trucks.models import FoodTruck

from .documents import build_document
from .es_client import es_client
from .indexes import INDEX_NAME

logger = logging.getLogger(__name__)


def index_truck(truck: FoodTruck):
    """Index (or re-index) a single truck. Uses the truck's DB id as the ES document id."""
    es_client.index(index=INDEX_NAME, id=truck.id, document=build_document(truck))


def bulk_index_trucks(queryset=None):
    """
    Bulk-index all (or a given queryset of) trucks into Elasticsearch.
    Far more efficient than calling index_truck() in a loop for many records.

    Returns (success_count, error_count).
    """
    queryset = queryset if queryset is not None else FoodTruck.objects.all()
    actions = (
        {
            "_index": INDEX_NAME,
            "_id": truck.id,
            "_source": build_document(truck),
        }
        for truck in queryset.iterator()
    )
    success_count, errors = bulk(
        es_client, actions, stats_only=False, raise_on_error=False
    )
    error_count = len(errors)
    logger.info(
        "Bulk indexed trucks into Elasticsearch",
        extra={"success_count": success_count, "error_count": error_count},
    )
    return success_count, error_count
