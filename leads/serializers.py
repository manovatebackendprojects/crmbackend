from rest_framework import serializers
from .models import Lead, LeadNote, LeadActivity

class LeadNoteSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='created_by.email', read_only=True)
    date = serializers.DateTimeField(source='created_at', read_only=True)
    
    class Meta:
        model = LeadNote
        fields = ['id', 'text', 'author', 'date']
        read_only_fields = ['id', 'author', 'date']


class LeadActivitySerializer(serializers.ModelSerializer):
    created_by_email = serializers.CharField(source='created_by.email', read_only=True)
    
    class Meta:
        model = LeadActivity
        fields = ['id', 'activity_type', 'description', 'activity_date', 'created_by_email', 'created_at']
        read_only_fields = ['id', 'created_by_email', 'created_at']


class LeadSerializer(serializers.ModelSerializer):
    lead_notes = LeadNoteSerializer(many=True, read_only=True)
    activities = LeadActivitySerializer(many=True, read_only=True)
    owner_email = serializers.CharField(source='owner.email', read_only=True)
    
    class Meta:
        model = Lead
        fields = [
            'id', 'name', 'email', 'phone', 'company', 'position',
            'stage', 'status', 'source', 'value', 'notes', 'image',
            'owner', 'owner_email', 'created_at', 'updated_at',
            'lead_notes', 'activities'
        ]
        read_only_fields = ['id', 'owner', 'owner_email', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # Set owner from request context
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class LeadListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list views"""
    owner_email = serializers.CharField(source='owner.email', read_only=True)
    
    class Meta:
        model = Lead
        fields = [
            'id', 'name', 'email', 'phone', 'company', 'position',
            'stage', 'status', 'source', 'value', 'owner_email', 'created_at'
        ]
        read_only_fields = ['id', 'owner_email', 'created_at']