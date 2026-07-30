from django.core.management.base import BaseCommand

from core.services.automation_service import (
    process_pending_applications,
)


class Command(BaseCommand):
    help = "Process all pending job applications"

    def handle(self, *args, **options):
        count = process_pending_applications()

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully processed {count} applications."
            )
        )