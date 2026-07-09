from django.core.management.base import BaseCommand

from config.celery import debug_task


class Command(BaseCommand):
    help = "Send a test task to Celery."

    def handle(self, *args, **options):
        result = debug_task.delay()
        self.stdout.write(self.style.SUCCESS(f"Celery task queued: {result.id}"))
