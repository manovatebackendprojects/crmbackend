# Models for calendar
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Event(models.Model):
    EVENT_CATEGORY = (
        ('event', 'Event'),
        ('task', 'Task'),
        ('meeting', 'Meeting'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    # Calendar time slots (Figma based)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    category = models.CharField(
        max_length=20,
        choices=EVENT_CATEGORY,
        default='event'
    )

    # Linking with other modules
    task_id = models.IntegerField(blank=True, null=True)
    meeting_id = models.IntegerField(blank=True, null=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='calendar_events'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_datetime']

    def __str__(self):
        return f"{self.title} ({self.start_datetime})"
