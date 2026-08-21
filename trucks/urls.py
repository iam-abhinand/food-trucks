from rest_framework.routers import DefaultRouter

from .views import FoodTruckViewSet

router = DefaultRouter()
router.register(r"trucks", FoodTruckViewSet, basename="truck")

urlpatterns = router.urls
