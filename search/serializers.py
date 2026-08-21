from rest_framework import serializers


class SearchQuerySerializer(serializers.Serializer):
    q = serializers.CharField(min_length=1, max_length=100)


class SearchResultSerializer(serializers.Serializer):
    db_id = serializers.IntegerField()
    applicant = serializers.CharField()
    food_items = serializers.CharField()
    facility_type = serializers.CharField()
    status = serializers.CharField()
    address = serializers.CharField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    score = serializers.FloatField()
