"""
Thin HTTP client for DataSF's Mobile Food Facility Permit dataset.
Responsible only for fetching raw JSON — no parsing, mapping, or DB logic here.
"""

import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class DataSFClientError(Exception):
    """Raised when the DataSF API request fails or returns an unexpected response."""


def fetch_food_trucks(limit: int = 1000) -> list[dict]:
    """
    Fetch food truck permit records from the DataSF Socrata API.
    Args:
        limit: max number of records to fetch in one call (Socrata default cap is 1000
        unless a higher limit is explicitly requested).
    Returns:
        A list of raw record dicts, exactly as returned by the API.
    Raises:
        DataSFClientError: if the request fails, times out,
        or the response is not valid JSON.
    """
    url = settings.DATASF_FOOD_TRUCKS_ENDPOINT
    params = {"$limit": limit}

    logger.info("Fetching food truck data from DataSF", extra={"url": url, "limit": limit})

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.error("DataSF request failed", extra={"error": str(exc)})
        raise DataSFClientError(f"Failed to fetch data from DataSF: {exc}") from exc

    try:
        data = response.json()
    except ValueError as exc:
        logger.error("DataSF response was not valid JSON", extra={"error": str(exc)})
        raise DataSFClientError(f"Invalid JSON from DataSF: {exc}") from exc

    logger.info("Fetched food truck records from DataSF", extra={"record_count": len(data)})
    return data
