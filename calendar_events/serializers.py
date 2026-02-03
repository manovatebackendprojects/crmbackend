from rest_framework import serializers
from .models import CalendarEvent, EventAttendee, EventReminder
from django.contrib.auth import get_user_model

User = get_user_model()


class EventAttendeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventAttendee
        fields = ['id', 'email', 'name', 'status', 'responded_at']
        read_only_fields = ['id', 'responded_at']


class EventReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventReminder
        fields = ['id', 'reminder_time', 'reminder_type', 'is_sent', 'sent_at']
        read_only_fields = ['id', 'is_sent', 'sent_at']


class CalendarEventSerializer(serializers.ModelSerializer):
    attendee_records = EventAttendeeSerializer(many=True, read_only=True)
    reminders = EventReminderSerializer(many=True, read_only=True)
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    duration = serializers.SerializerMethodField()
    attendees_list = serializers.SerializerMethodField()
    is_upcoming = serializers.BooleanField(read_only=True)
    
    # Frontend field mapping
    date = serializers.DateField(source='event_date')
    start = serializers.TimeField(source='start_time', format='%H:%M')
    end = serializers.TimeField(source='end_time', format='%H:%M')
    type = serializers.CharField(source='event_type')
    desc = serializers.CharField(source='description', required=False, allow_blank=True)
    attendees = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = CalendarEvent
        fields = [
            'id',
            # Backend field names
            'title', 'description', 'event_type', 'event_date', 'start_time', 
            'end_time', 'location', 'reminder_set', 'reminder_minutes_before',
            'attendee_records', 'reminders', 'owner_name', 'created_at', 'updated_at',
            'duration', 'attendees_list', 'is_upcoming',
            # Frontend field names (mapped)
            'date', 'start', 'end', 'type', 'desc', 'attendees'
        ]
        read_only_fields = ['id', 'owner_name', 'attendee_records', 'reminders', 'created_at', 'updated_at']
    
    def get_duration(self, obj):
        """Return duration as string like '60 min'"""
        minutes = obj.get_duration()
        return f"{minutes} min"
    
    def get_attendees_list(self, obj):
        """Return parsed attendees list"""
        return obj.get_attendees_list()
    
    def validate(self, data):
        """Validate event times"""
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        
        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError({
                'end_time': 'End time must be after start time.'
            })
        
        return data


class CalendarEventListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    duration = serializers.SerializerMethodField()
    attendees_list = serializers.SerializerMethodField()
    
    # Frontend field mapping
    date = serializers.DateField(source='event_date')
    start = serializers.TimeField(source='start_time', format='%H:%M')
    type = serializers.CharField(source='event_type')
    desc = serializers.CharField(source='description')
    
    class Meta:
        model = CalendarEvent
        fields = [
            'id', 'title', 'description', 'event_type', 'event_date', 'start_time',
            'location', 'owner_name', 'created_at', 'updated_at',
            'duration', 'attendees_list',
            # Frontend fields
            'date', 'start', 'type', 'desc'
        ]
        read_only_fields = ['id', 'owner_name', 'created_at', 'updated_at']
    
    def get_duration(self, obj):
        minutes = obj.get_duration()
        return f"{minutes} min"
    
    def get_attendees_list(self, obj):
        return obj.get_attendees_list()