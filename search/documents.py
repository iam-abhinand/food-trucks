"""
Converts a FoodTruck model instance into an Elasticsearch document dict.
"""

from trucks.models import FoodTruck


def build_document(truck: FoodTruck) -> dict:
    return {
        "db_id": truck.id,
        "applicant": truck.applicant,
        "food_items": truck.food_items,
        "facility_type": truck.facility_type,
        "status": truck.status,
        "address": truck.address,
        "latitude": float(truck.latitude),
        "longitude": float(truck.longitude),
    }
