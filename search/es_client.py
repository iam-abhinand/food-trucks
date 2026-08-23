"""
Shared Elasticsearch client instance, configured from settings.
"""

from django.conf import settings
from elasticsearch import Elasticsearch

if settings.ELASTICSEARCH_USERNAME and settings.ELASTICSEARCH_PASSWORD:
    es_client = Elasticsearch(
        hosts=[settings.ELASTICSEARCH_HOST],
        basic_auth=(settings.ELASTICSEARCH_USERNAME, settings.ELASTICSEARCH_PASSWORD),
    )
else:
    # Local dev: security disabled, no auth needed.
    es_client = Elasticsearch(hosts=[settings.ELASTICSEARCH_HOST])
