"""
Celery task for syncing food truck data from DataSF into our database.
"""

import logging

from celery import shared_task

from trucks.models import FoodTruck

from .datasf_client import DataSFClientError, fetch_food_trucks
from .mappers import map_datasf_record

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def sync_food_trucks(self, limit: int = 1000):
    """
    Fetch food truck records from DataSF and upsert them into the database.

    Upserting (rather than delete-and-recreate) means existing records are
    updated in place using `external_id` as the natural key, and genuinely
    new trucks are created. Records that fail to fetch or parse are skipped
    and logged, not allowed to abort the whole sync.

    Returns a summary dict of what happened, useful for logging/monitoring.
    """
    logger.info("Starting food truck sync")

    try:
        raw_records = fetch_food_trucks(limit=limit)
    except DataSFClientError as exc:
        logger.error(
            "Food truck sync aborted: could not fetch data", extra={"error": str(exc)}
        )
        # Retry with exponential-ish backoff via Celery's built-in retry delay,
        # in case this was a transient network/API issue.
        raise self.retry(exc=exc)

    created_count = 0
    updated_count = 0
    skipped_count = 0

    for raw_record in raw_records:
        mapped = map_datasf_record(raw_record)
        if mapped is None:
            skipped_count += 1
            continue

        external_id = mapped.pop("external_id")
        _, created = FoodTruck.objects.update_or_create(
            external_id=external_id,
            defaults=mapped,
        )
        if created:
            created_count += 1
        else:
            updated_count += 1

    summary = {
        "total_fetched": len(raw_records),
        "created": created_count,
        "updated": updated_count,
        "skipped": skipped_count,
    }
    logger.info(
        "Food truck sync completed",
        extra={
            "total_fetched": summary["total_fetched"],
            "records_created": summary["created"],
            "records_updated": summary["updated"],
            "records_skipped": summary["skipped"],
        },
    )
    return summary
