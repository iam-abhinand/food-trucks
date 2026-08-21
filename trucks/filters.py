import django_filters

from .models import FoodTruck


class FoodTruckFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=FoodTruck.Status.choices)
    facility_type = django_filters.CharFilter(lookup_expr="icontains")
    applicant = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = FoodTruck
        fields = ["status", "facility_type", "applicant"]  # noqa: RUF012
