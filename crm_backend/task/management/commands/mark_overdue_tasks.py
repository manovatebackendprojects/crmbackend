from django.core.management.base import BaseCommand
from django.utils import timezone
from task.models import Task


class Command(BaseCommand):
    help = 'Mark overdue tasks automatically'

    def handle(self, *args, **kwargs):
        overdue_tasks = Task.objects.filter(
            status='PENDING',
            due_date__lt=timezone.now()
        )

        updated = overdue_tasks.update(status='OVERDUE')
        self.stdout.write(self.style.SUCCESS(f"{updated} tasks marked as overdue"))
