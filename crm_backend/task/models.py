from django.db import models
from django.conf import settings
from django.utils import timezone

User = settings.AUTH_USER_MODEL


class Task(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('OVERDUE', 'Overdue'),
    )

    title = models.CharField(max_length=255)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE)
    due_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    created_at = models.DateTimeField(auto_now_add=True)

    def is_overdue(self):
        return self.status != 'COMPLETED' and self.due_date < timezone.now()

    def mark_overdue(self):
        if self.is_overdue():
            self.status = 'OVERDUE'
            self.save()
