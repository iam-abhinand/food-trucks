from rest_framework import serializers

from .models import FoodTruck


class FoodTruckSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodTruck
        fields = [  # noqa: RUF012
            "id",
            "external_id",
            "applicant",
            "facility_type",
            "address",
            "permit_number",
            "status",
            "food_items",
            "latitude",
            "longitude",
            "schedule_url",
            "expiration_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            fields  # this API is read-only for now; writes happen via ingestion
        )
