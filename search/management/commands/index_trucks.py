from django.core.management.base import BaseCommand

from search.indexes import create_index_if_not_exists
from search.indexing import bulk_index_trucks


class Command(BaseCommand):
    help = "Create the Elasticsearch index and bulk-index all food trucks from the database."

    def handle(self, *args, **options):
        self.stdout.write("Ensuring Elasticsearch index exists...")
        create_index_if_not_exists()
        self.stdout.write("Bulk indexing trucks...")
        success_count, error_count = bulk_index_trucks()
        self.stdout.write(
            self.style.SUCCESS(
                f"Indexed {success_count} trucks ({error_count} errors)."
            )
        )
