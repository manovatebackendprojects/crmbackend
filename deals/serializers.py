from rest_framework import serializers
from .models import Deal, DealComment, DealAttachment
from django.contrib.auth import get_user_model

User = get_user_model()


class DealCommentSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = DealComment
        fields = ['id', 'deal', 'text', 'created_by', 'created_by_name', 
                  'created_by_username', 'created_at']
        read_only_fields = ['id', 'deal', 'created_by', 'created_at']


class DealAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = DealAttachment
        fields = ['id', 'deal', 'file', 'file_url', 'file_name', 'file_size', 
                  'uploaded_by', 'uploaded_by_name', 'uploaded_at']
        read_only_fields = ['id', 'deal', 'uploaded_by', 'uploaded_at', 'file_size']
    
    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and hasattr(obj.file, 'url'):
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None
    
    def validate_file(self, value):
        """Validate file size (max 5MB)"""
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("File size exceeds 5MB limit.")
        return value


class DealSerializer(serializers.ModelSerializer):
    activity = serializers.SerializerMethodField()
    comments_list = DealCommentSerializer(source='comments', many=True, read_only=True)
    attachments_list = DealAttachmentSerializer(source='attachments', many=True, read_only=True)
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    
    class Meta:
        model = Deal
        fields = ['id', 'title', 'description', 'client', 'stage', 'status', 
                  'amount', 'due_date', 'assignee_initials', 'owner', 'owner_name',
                  'activity', 'comments_list', 'attachments_list',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']
    
    def get_activity(self, obj):
        """Return activity counts and lists"""
        return {
            'comments': obj.comments.count(),
            'attachments': obj.attachments.count(),
            'commentsList': DealCommentSerializer(obj.comments.all(), many=True).data,
            'attachmentsList': DealAttachmentSerializer(
                obj.attachments.all(), 
                many=True, 
                context=self.context
            ).data,
        }
    
    def validate_stage(self, value):
        """Validate stage transitions"""
        if self.instance:
            # Prevent moving deals out of 'Status' stage
            if self.instance.stage == 'Status' and value != 'Status':
                raise serializers.ValidationError(
                    "Closed deals cannot be moved back to the pipeline."
                )
            
            # Only allow moving to 'Status' from 'Revenue'
            if value == 'Status' and self.instance.stage != 'Revenue':
                raise serializers.ValidationError(
                    "Deals can only be closed from the 'Revenue' stage."
                )
        
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        # If moving to Status stage, status must be Won or Lost
        if data.get('stage') == 'Status':
            status = data.get('status', self.instance.status if self.instance else 'Open')
            if status not in ['Won', 'Lost']:
                raise serializers.ValidationError({
                    'status': 'Status must be "Won" or "Lost" when in Status stage.'
                })
        
        return data


class DealListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    activity = serializers.SerializerMethodField()
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    
    class Meta:
        model = Deal
        fields = ['id', 'title', 'description', 'client', 'stage', 'status', 
                  'amount', 'due_date', 'assignee_initials', 'owner_name',
                  'activity', 'created_at', 'updated_at']
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']
    
    def get_activity(self, obj):
        """Return only counts for list view performance"""
        return obj.get_activity_counts()