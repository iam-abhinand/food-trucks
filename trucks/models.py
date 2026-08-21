from django.db import models


class FoodTruck(models.Model):
    """
    Represents a single food truck/cart permit record from DataSF's
    Mobile Food Facility Permit dataset.

    `external_id` maps to DataSF's `objectid` — used to upsert records
    on each sync so we don't create duplicates on re-ingestion.
    """

    class Status(models.TextChoices):
        APPROVED = "APPROVED", "Approved"
        REQUESTED = "REQUESTED", "Requested"
        EXPIRED = "EXPIRED", "Expired"
        SUSPEND = "SUSPEND", "Suspended"
        ISSUED = "ISSUED", "Issued"
        OTHER = "OTHER", "Other"

    external_id = models.CharField(max_length=50, unique=True, db_index=True)
    applicant = models.CharField(max_length=255)
    facility_type = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=255, blank=True)
    permit_number = models.CharField(max_length=50, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.OTHER, db_index=True
    )
    food_items = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    schedule_url = models.URLField(blank=True)
    expiration_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [  # noqa: RUF012
            models.Index(fields=["latitude", "longitude"]),
        ]
        ordering = ["applicant"]  # noqa: RUF012

    def __str__(self):
        return f"{self.applicant} ({self.status})"
