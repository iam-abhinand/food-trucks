from rest_framework import viewsets

from .filters import FoodTruckFilter
from .models import FoodTruck
from .serializers import FoodTruckSerializer


class FoodTruckViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only API for browsing food truck data.
    list:   GET /api/v1/trucks/           — paginated, filterable list
    retrieve: GET /api/v1/trucks/{id}/    — single truck detail
    """

    queryset = FoodTruck.objects.all()
    serializer_class = FoodTruckSerializer
    filterset_class = FoodTruckFilter
