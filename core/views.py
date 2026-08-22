import logging

from django.core.cache import cache
from django.db import connection
from rest_framework.response import Response
from rest_framework.views import APIView

from search.es_client import es_client

logger = logging.getLogger(__name__)


class HealthCheckView(APIView):
    """
    GET /health/

    Checks connectivity to core dependencies: database, cache, and search.
    Returns 200 if all are healthy, 503 if any are down.
    """

    permission_classes = []  # noqa: RUF012
    # publicly accessible, no auth required for health checks
    authentication_classes = []  # noqa: RUF012

    def get(self, request):
        checks = {
            "database": self._check_database(),
            "cache": self._check_cache(),
            "elasticsearch": self._check_elasticsearch(),
        }
        all_healthy = all(checks.values())
        status_code = 200 if all_healthy else 503
        if not all_healthy:
            logger.warning("Health check failed", extra=checks)
        return Response(
            {"status": "healthy" if all_healthy else "unhealthy", "checks": checks},
            status=status_code,
        )

    def _check_database(self) -> bool:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return True
        except Exception:
            logger.exception("Database health check failed")
            return False

    def _check_cache(self) -> bool:
        try:
            cache.set("health_check", "ok", timeout=5)
            return cache.get("health_check") == "ok"
        except Exception:
            logger.exception("Cache health check failed")
            return False

    def _check_elasticsearch(self) -> bool:
        try:
            return es_client.ping()
        except Exception:
            logger.exception("Elasticsearch health check failed")
            return False
