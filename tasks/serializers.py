from rest_framework import serializers
from .models import Task, TaskComment, TaskAttachment
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    initials = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'initials']
    
    def get_initials(self, obj):
        if obj.first_name and obj.last_name:
            return f"{obj.first_name[0]}{obj.last_name[0]}".upper()
        return obj.email[:2].upper()


class TaskCommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    initials = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    
    class Meta:
        model = TaskComment
        fields = ['id', 'text', 'author', 'date', 'initials', 'created_at']
        read_only_fields = ['created_at']
    
    def get_author(self, obj):
        return obj.author.first_name or obj.author.email.split('@')[0]
    
    def get_initials(self, obj):
        if obj.author.first_name and obj.author.last_name:
            return f"{obj.author.first_name[0]}{obj.author.last_name[0]}".upper()
        return obj.author.email[:2].upper()
    
    def get_date(self, obj):
        return obj.created_at.strftime('%Y-%m-%d')


class TaskAttachmentSerializer(serializers.ModelSerializer):
    size = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    data = serializers.SerializerMethodField()
    
    class Meta:
        model = TaskAttachment
        fields = ['id', 'file', 'file_name', 'size', 'date', 'type', 'data', 'created_at']
        read_only_fields = ['created_at']
    
    def get_size(self, obj):
        return obj.file_size
    
    def get_date(self, obj):
        return obj.created_at.strftime('%Y-%m-%d')
    
    def get_type(self, obj):
        import mimetypes
        return mimetypes.guess_type(obj.file.name)[0] or 'application/octet-stream'
    
    def get_data(self, obj):
        # Return file URL instead of base64 (for performance)
        request = self.context.get('request')
        if request and obj.file:
            return request.build_absolute_uri(obj.file.url)
        return None


class TaskSerializer(serializers.ModelSerializer):
    assignee = serializers.SerializerMethodField()
    activity = serializers.SerializerMethodField()
    commentsList = TaskCommentSerializer(source='comments', many=True, read_only=True)
    attachmentsList = TaskAttachmentSerializer(source='attachments', many=True, read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'client', 'priority', 
            'due_date', 'stage', 'assignee', 'image', 
            'priority_color', 'is_overdue', 'activity',
            'commentsList', 'attachmentsList',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'priority_color', 'is_overdue']
    
    def get_assignee(self, obj):
        if obj.assigned_to:
            initials = obj.assigned_to.first_name[:1] + obj.assigned_to.last_name[:1] if obj.assigned_to.first_name else obj.assigned_to.email[:2]
            return [{
                'initials': initials.upper(),
                'color': 'bg-purple-500'
            }]
        return []
    
    def get_activity(self, obj):
        return {
            'comments': obj.comments.count(),
            'attachments': obj.attachments.count(),
            'commentsList': TaskCommentSerializer(obj.comments.all(), many=True).data,
            'attachmentsList': TaskAttachmentSerializer(
                obj.attachments.all(), 
                many=True, 
                context=self.context
            ).data,
        }


class TaskCreateUpdateSerializer(serializers.ModelSerializer):
    assigneeInitials = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'client', 'priority',
            'due_date', 'stage', 'assigneeInitials', 'image'
        ]
    
    def create(self, validated_data):
        validated_data.pop('assigneeInitials', None)
        validated_data['created_by'] = self.context['request'].user
        validated_data['assigned_to'] = self.context['request'].user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        validated_data.pop('assigneeInitials', None)
        return super().update(instance, validated_data)