# Serializers for calendar
from rest_framework import serializers
from .models import Event


class EventSerializer(serializers.ModelSerializer):
    duration_minutes = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id',
            'title',
            'description',
            'start_datetime',
            'end_datetime',
            'duration_minutes',
            'category',
            'task_id',
            'meeting_id',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_duration_minutes(self, obj):
        return int((obj.end_datetime - obj.start_datetime).total_seconds() / 60)
