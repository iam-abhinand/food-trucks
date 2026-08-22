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
        read_only_fields = fields  # this API is read-only for now; writes happen via ingestion


class FoodTruckWithDistanceSerializer(FoodTruckSerializer):
    """
    Extends FoodTruckSerializer with a computed distance_km field, used only
    by the /nearby endpoint. distance_km is attached to each model instance
    as a plain Python attribute before serialization (see NearbyFoodTruckView).
    """

    distance_km = serializers.FloatField(read_only=True)

    class Meta(FoodTruckSerializer.Meta):
        fields = FoodTruckSerializer.Meta.fields + ["distance_km"]


class NearbyQuerySerializer(serializers.Serializer):
    """
    Validates query params for the /nearby endpoint.
    """

    lat = serializers.FloatField(min_value=-90, max_value=90)
    lng = serializers.FloatField(min_value=-180, max_value=180)
    radius_km = serializers.FloatField(min_value=0.1, max_value=50, default=2.0)
