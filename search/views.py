import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from .queries import search_trucks
from .serializers import SearchQuerySerializer, SearchResultSerializer

logger = logging.getLogger(__name__)


class TruckSearchView(APIView):
    """
    GET /api/v1/search/?q=taco
    Autocomplete-style search across truck names and food items,
    backed by Elasticsearch.
    """

    def get(self, request):
        query_serializer = SearchQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        query = query_serializer.validated_data["q"]
        raw_results = search_trucks(query)
        logger.info(
            "Truck search executed",
            extra={"query": query, "result_count": len(raw_results)},
        )
        serializer = SearchResultSerializer(raw_results, many=True)
        return Response(serializer.data)
