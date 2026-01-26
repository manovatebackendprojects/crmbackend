from django.db import models
from leads.models import Lead

class Task(models.Model):
    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("COMPLETED", "Completed"),
    )

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=200)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
