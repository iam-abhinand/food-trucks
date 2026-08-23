import logging

from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .tasks import sync_food_trucks

logger = logging.getLogger(__name__)


class TriggerSyncView(APIView):
    """
    POST /api/v1/sync/
    Triggers a DataSF sync. Runs asynchronously via Celery when a worker is
    available (CELERY_TASK_ALWAYS_EAGER=False, the normal/production setup
    with a dedicated worker process). Falls back to running synchronously,
    inline in the request, when no worker is available — e.g. on free-tier
    hosting without a background worker service. This keeps the endpoint
    usable in both environments without duplicating logic.
    """

    permission_classes = [IsAuthenticated]  # noqa: RUF012
    throttle_classes = [ScopedRateThrottle]  # noqa: RUF012
    throttle_scope = "sync"

    def post(self, request):
        limit = int(request.data.get("limit", 1000))

        if getattr(settings, "SYNC_RUNS_SYNCHRONOUSLY", False):
            logger.info(
                "Running sync synchronously (no worker available)",
                extra={"user_id": request.user.id, "limit": limit},
            )
            result = sync_food_trucks(limit=limit)
            return Response(
                {"message": "Sync completed.", "result": result},
                status=200,
            )
        task = sync_food_trucks.delay(limit=limit)
        logger.info(
            "Manual sync triggered via API (async)",
            extra={"user_id": request.user.id, "task_id": task.id, "limit": limit},
        )
        return Response(
            {"message": "Sync started.", "task_id": task.id},
            status=202,
        )
