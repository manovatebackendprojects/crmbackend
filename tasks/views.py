from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Task, TaskComment, TaskAttachment
from .serializers import (
    TaskSerializer, 
    TaskCreateUpdateSerializer,
    TaskCommentSerializer,
    TaskAttachmentSerializer
)


class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        # Users see only their tasks or tasks assigned to them
        user = self.request.user
        return Task.objects.filter(created_by=user) | Task.objects.filter(assigned_to=user)
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TaskCreateUpdateSerializer
        return TaskSerializer
    
    @extend_schema(tags=['Tasks'])
    def list(self, request):
        """Get all tasks for the authenticated user"""
        queryset = self.get_queryset()
        
        # Filter by stage (for tabs)
        stage = request.query_params.get('stage')
        if stage:
            queryset = queryset.filter(stage=stage)
        
        # Filter by priority
        priority = request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        # Search
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search) | \
                       queryset.filter(description__icontains=search) | \
                       queryset.filter(client__icontains=search)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(tags=['Tasks'])
    def create(self, request):
        """Create a new task"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Return full task data
        task = Task.objects.get(id=serializer.data['id'])
        response_serializer = TaskSerializer(task, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(tags=['Tasks'])
    def update(self, request, pk=None):
        """Update a task"""
        task = self.get_object()
        serializer = self.get_serializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Return full task data
        response_serializer = TaskSerializer(task, context={'request': request})
        return Response(response_serializer.data)
    
    @extend_schema(tags=['Tasks'])
    def destroy(self, request, pk=None):
        """Delete a task"""
        task = self.get_object()
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @extend_schema(tags=['Tasks'], methods=['POST'])
    @action(detail=True, methods=['post'])
    def comments(self, request, pk=None):
        """Add a comment to a task"""
        task = self.get_object()
        
        comment = TaskComment.objects.create(
            task=task,
            author=request.user,
            text=request.data.get('text', '')
        )
        
        serializer = TaskCommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(tags=['Tasks'], methods=['POST'])
    @action(detail=True, methods=['post'])
    def attachments(self, request, pk=None):
        """Add an attachment to a task"""
        task = self.get_object()
        
        file = request.FILES.get('file')
        if not file:
            return Response(
                {'detail': 'No file provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate file size
        file_size = file.size / 1024  # KB
        if file_size > 1024:
            size_str = f"{file_size / 1024:.1f} MB"
        else:
            size_str = f"{file_size:.1f} KB"
        
        attachment = TaskAttachment.objects.create(
            task=task,
            file=file,
            file_name=file.name,
            file_size=size_str,
            uploaded_by=request.user
        )
        
        serializer = TaskAttachmentSerializer(attachment, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(tags=['Tasks'], methods=['DELETE'])
    @action(detail=True, methods=['delete'], url_path='attachments/(?P<attachment_id>[^/.]+)')
    def delete_attachment(self, request, pk=None, attachment_id=None):
        """Delete an attachment"""
        task = self.get_object()
        
        try:
            attachment = task.attachments.get(id=attachment_id)
            attachment.file.delete()  # Delete file from storage
            attachment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except TaskAttachment.DoesNotExist:
            return Response(
                {'detail': 'Attachment not found'},
                status=status.HTTP_404_NOT_FOUND
            )