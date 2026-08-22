from django.urls import path

from .views import TriggerSyncView

urlpatterns = [
    path("sync/", TriggerSyncView.as_view(), name="trigger-sync"),
]
