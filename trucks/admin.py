from django.contrib import admin

from .models import FoodTruck


@admin.register(FoodTruck)
class FoodTruckAdmin(admin.ModelAdmin):
    list_display = ("applicant", "facility_type", "status", "address")
    list_filter = ("status", "facility_type")
    search_fields = ("applicant", "address", "food_items")
