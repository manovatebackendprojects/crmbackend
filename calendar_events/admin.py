from django.contrib import admin
from .models import CalendarEvent, EventAttendee, EventReminder


class EventAttendeeInline(admin.TabularInline):
    model = EventAttendee
    extra = 0
    readonly_fields = ['responded_at']


class EventReminderInline(admin.TabularInline):
    model = EventReminder
    extra = 0
    readonly_fields = ['is_sent', 'sent_at']


@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_date', 'start_time', 'event_type', 'owner', 'created_at']
    list_filter = ['event_type', 'event_date', 'created_at']
    search_fields = ['title', 'description', 'location', 'owner__email']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [EventAttendeeInline, EventReminderInline]
    
    fieldsets = (
        ('Event Information', {
            'fields': ('title', 'description', 'event_type', 'location')
        }),
        ('Date & Time', {
            'fields': ('event_date', 'start_time', 'end_time', 'duration_minutes')
        }),
        ('Attendees', {
            'fields': ('attendees',),
            'classes': ('collapse',)
        }),
        ('Reminders', {
            'fields': ('reminder_set', 'reminder_minutes_before'),
            'classes': ('collapse',)
        }),
        ('Ownership', {
            'fields': ('owner',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(EventAttendee)
class EventAttendeeAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'event', 'status', 'responded_at']
    list_filter = ['status', 'responded_at']
    search_fields = ['email', 'name', 'event__title']
    readonly_fields = ['responded_at']


@admin.register(EventReminder)
class EventReminderAdmin(admin.ModelAdmin):
    list_display = ['event', 'reminder_time', 'reminder_type', 'is_sent', 'sent_at']
    list_filter = ['reminder_type', 'is_sent', 'reminder_time']
    search_fields = ['event__title']
    readonly_fields = ['is_sent', 'sent_at']