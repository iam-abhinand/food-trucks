from django.urls import path

from .views import TruckSearchView

urlpatterns = [
    path("search/", TruckSearchView.as_view(), name="truck-search"),
]
