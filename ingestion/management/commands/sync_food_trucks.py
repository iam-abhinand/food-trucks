"""
Management command to manually trigger a food truck sync from the CLI,
without needing to go through the Django shell or Celery.
"""

from django.core.management.base import BaseCommand

from ingestion.tasks import sync_food_trucks


class Command(BaseCommand):
    help = "Fetch and upsert food truck data from DataSF."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=1000,
            help="Max number of records to fetch from DataSF (default: 1000).",
        )

    def handle(self, *args, **options):
        limit = options["limit"]
        self.stdout.write(f"Syncing food trucks (limit={limit})...")

        result = sync_food_trucks(limit=limit)

        self.stdout.write(
            self.style.SUCCESS(
                f"Sync complete: {result['created']} created, "
                f"{result['updated']} updated, {result['skipped']} skipped "
                f"(of {result['total_fetched']} fetched)."
            )
        )
