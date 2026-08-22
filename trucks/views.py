import logging

from django.core.cache import cache
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.geo import bounding_box, haversine_distance_km

from .filters import FoodTruckFilter
from .models import FoodTruck
from .serializers import FoodTruckSerializer, FoodTruckWithDistanceSerializer, NearbyQuerySerializer

logger = logging.getLogger(__name__)


class FoodTruckViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only API for browsing food truck data.
    list:   GET /api/v1/trucks/             — paginated, filterable list
    retrieve: GET /api/v1/trucks/{id}/      — single truck detail
    nearby: GET /api/v1/trucks/nearby/      — trucks near a given point
    """

    queryset = FoodTruck.objects.all()
    serializer_class = FoodTruckSerializer
    filterset_class = FoodTruckFilter

    @action(detail=False, methods=["get"])
    def nearby(self, request):
        query_serializer = NearbyQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        lat = query_serializer.validated_data["lat"]
        lng = query_serializer.validated_data["lng"]
        radius_km = query_serializer.validated_data["radius_km"]

        cache_key = f"nearby:{lat:.4f}:{lng:.4f}:{radius_km:.2f}"
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            logger.info("Nearby search cache hit", extra={"cache_key": cache_key})
            return Response(cached_result)

        box = bounding_box(lat, lng, radius_km)

        # Cheap DB-level pre-filter using the indexed lat/lng columns,
        # narrows down candidates before the more expensive Haversine pass.
        candidates = FoodTruck.objects.filter(
            latitude__gte=box["min_lat"],
            latitude__lte=box["max_lat"],
            longitude__gte=box["min_lon"],
            longitude__lte=box["max_lon"],
        )

        # Precise distance filtering + sorting in Python.
        results = []
        for truck in candidates:
            distance = haversine_distance_km(lat, lng, float(truck.latitude), float(truck.longitude))
            if distance <= radius_km:
                truck.distance_km = round(distance, 3)
                results.append(truck)

        results.sort(key=lambda t: t.distance_km)

        serializer = FoodTruckWithDistanceSerializer(results, many=True)
        data = serializer.data

        cache.set(cache_key, data, timeout=300)  # cache for 5 minutes
        logger.info(
            "Nearby search executed",
            extra={
                "lat": lat,
                "lng": lng,
                "radius_km": radius_km,
                "candidate_count": candidates.count(),
                "result_count": len(results),
            },
        )

        return Response(data)
