from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()

class CalendarEvent(models.Model):
    EVENT_TYPE_CHOICES = [
        ('meeting', 'Meeting'),
        ('event', 'Event'),
        ('reminder', 'Task Reminder'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, default='meeting')
    
    # Date & Time
    event_date = models.DateField(help_text="Date of the event", null=True, blank=True)
    start_time = models.TimeField(help_text="Start time (HH:MM format)", null=True, blank=True)
    end_time = models.TimeField(help_text="End time (HH:MM format)", null=True, blank=True)
    duration_minutes = models.IntegerField(default=60, validators=[MinValueValidator(15)])
    
    # Location
    location = models.CharField(max_length=255, blank=True, null=True)
    
    # Guest Management
    attendees = models.TextField(blank=True, null=True, help_text="Comma-separated email addresses or JSON list")
    
    # Ownership & Timestamps
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='calendar_events', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Notification
    reminder_set = models.BooleanField(default=True, help_text="Send reminder notification")
    reminder_minutes_before = models.IntegerField(default=15, help_text="Minutes before event to send reminder")
    
    class Meta:
        ordering = ['-event_date', '-start_time']
        indexes = [
            models.Index(fields=['owner', 'event_date']),
            models.Index(fields=['event_date', 'start_time']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.event_date} at {self.start_time}"
    
    def get_duration(self):
        """Calculate duration from start and end time"""
        from datetime import datetime, timedelta
        start = datetime.combine(self.event_date, self.start_time)
        end = datetime.combine(self.event_date, self.end_time)
        delta = end - start
        return int(delta.total_seconds() / 60)
    
    def get_attendees_list(self):
        """Parse attendees string into list"""
        if not self.attendees:
            return []
        if self.attendees.startswith('['):
            import json
            try:
                return json.loads(self.attendees)
            except:
                return self.attendees.split(',')
        return [email.strip() for email in self.attendees.split(',')]
    
    @property
    def is_upcoming(self):
        """Check if event is in the future"""
        from django.utils import timezone
        from datetime import datetime
        event_datetime = datetime.combine(self.event_date, self.start_time)
        return event_datetime > timezone.now()


class EventAttendee(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('tentative', 'Tentative'),
    ]
    
    event = models.ForeignKey(CalendarEvent, on_delete=models.CASCADE, related_name='attendee_records')
    email = models.EmailField()
    name = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    responded_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        unique_together = ['event', 'email']
        ordering = ['status', 'email']
    
    def __str__(self):
        return f"{self.email} - {self.event.title} ({self.status})"


class EventReminder(models.Model):
    REMINDER_TYPE_CHOICES = [
        ('email', 'Email'),
        ('notification', 'In-App Notification'),
        ('both', 'Both'),
    ]
    
    event = models.ForeignKey(CalendarEvent, on_delete=models.CASCADE, related_name='reminders')
    reminder_time = models.DateTimeField(help_text="When to send the reminder", null=True, blank=True)
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPE_CHOICES, default='notification')
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['reminder_time']
    
    def __str__(self):
        return f"Reminder for {self.event.title} at {self.reminder_time}"