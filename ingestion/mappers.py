"""
Transforms raw DataSF API records into FoodTruck model field dictionaries.
Kept separate from the fetch and save steps so mapping logic can be
unit tested with plain dicts, no network or DB required.
"""

import logging
from datetime import datetime

from django.utils import timezone

from trucks.models import FoodTruck

logger = logging.getLogger(__name__)

# Maps DataSF's raw status strings to our model's Status choices.
STATUS_MAP = {
    "APPROVED": FoodTruck.Status.APPROVED,
    "REQUESTED": FoodTruck.Status.REQUESTED,
    "EXPIRED": FoodTruck.Status.EXPIRED,
    "SUSPEND": FoodTruck.Status.SUSPEND,
    "ISSUED": FoodTruck.Status.ISSUED,
}


def _parse_expiration_date(raw_value: str | None):
    """
    Parse expirationdate from DataSF API response.
    Args:
        raw_value: The expirationdate value from the API response
    Returns:
        datetime object if parsing is successful, None otherwise
    """
    if not raw_value:
        return None
    try:
        parsed = datetime.fromisoformat(raw_value)
    except ValueError:
        logger.warning("Could not parse expirationdate", extra={"raw_value": raw_value})
        return None

    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed, timezone.get_default_timezone())
    return parsed


def map_datasf_record(record: dict) -> dict | None:
    """
    Convert a single raw DataSF record into a dict of FoodTruck field values.

    Returns None if the record is missing required fields (external id or
    coordinates), since such a record can't be meaningfully stored or
    geo-queried later.
    """
    external_id = record.get("objectid")
    latitude = record.get("latitude")
    longitude = record.get("longitude")

    if not external_id or not latitude or not longitude:
        logger.warning(
            "Skipping DataSF record missing required fields",
            extra={"objectid": external_id},
        )
        return None

    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except (TypeError, ValueError):
        logger.warning(
            "Skipping DataSF record with non-numeric coordinates",
            extra={
                "objectid": external_id,
                "latitude": latitude,
                "longitude": longitude,
            },
        )
        return None

    raw_status = (record.get("status") or "").upper()
    status = STATUS_MAP.get(raw_status, FoodTruck.Status.OTHER)

    return {
        "external_id": external_id,
        "applicant": record.get("applicant", "").strip() or "Unknown",
        "facility_type": record.get("facilitytype", ""),
        "address": record.get("address", ""),
        "permit_number": record.get("permit", ""),
        "status": status,
        "food_items": record.get("fooditems", ""),
        "latitude": latitude,
        "longitude": longitude,
        "schedule_url": record.get("schedule", ""),
        "expiration_date": _parse_expiration_date(record.get("expirationdate")),
    }
