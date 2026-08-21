from django.conf import settings
from elasticsearch import Elasticsearch

es_client = Elasticsearch(hosts=[settings.ELASTICSEARCH_HOST])
