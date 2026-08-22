import logging

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .tasks import sync_food_trucks

logger = logging.getLogger(__name__)


class TriggerSyncView(APIView):
    """
    POST /api/v1/sync/
    Triggers an asynchronous DataSF sync via Celery. Requires authentication
    since this consumes external API quota and writes to the database —
    it shouldn't be callable by anonymous users.
    """

    permission_classes = [IsAuthenticated]  # noqa: RUF012
    throttle_classes = [ScopedRateThrottle]  # noqa: RUF012
    throttle_scope = "sync"

    def post(self, request):
        limit = int(request.data.get("limit", 1000))
        task = sync_food_trucks.delay(limit=limit)
        logger.info(
            "Manual sync triggered via API",
            extra={"user_id": request.user.id, "task_id": task.id, "limit": limit},
        )
        return Response(
            {"message": "Sync started.", "task_id": task.id},
            status=202,
        )
